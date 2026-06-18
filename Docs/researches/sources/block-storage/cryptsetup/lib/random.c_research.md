# File Research: sources/block-storage/cryptsetup/lib/random.c

This file implements cryptsetup RNG access through kernel random devices and the crypto backend in FIPS mode.

Global state:
- `random_initialised`
- `urandom_fd` for `/dev/urandom`
- `random_fd` for `/dev/random`

Initialization:
- `crypt_random_init()` opens `/dev/urandom` read-only close-on-exec and `/dev/random` read-only nonblocking close-on-exec.
- Both descriptors are mandatory.
- On failure it closes any opened descriptors and returns `-ENOSYS`.
- Logs when running in FIPS mode.

Random data paths:
- `_get_urandom()` reads until the requested length is filled, retrying on `EINTR`; other read errors return `-EINVAL`.
- `_get_random()` waits with `select()` on `/dev/random`, prints entropy/progress warnings after a timeout, reads in 8-byte chunks, handles `EINTR` and nonblocking `EAGAIN/EWOULDBLOCK`, and fills the full buffer.
- `crypt_random_get()` chooses source by quality:
  - `CRYPT_RND_NORMAL`: `/dev/urandom`
  - `CRYPT_RND_SALT`: backend RNG in FIPS mode, otherwise `/dev/urandom`
  - `CRYPT_RND_KEY`: backend RNG in FIPS mode, otherwise default or context-selected `/dev/random` or `/dev/urandom`
- Unknown quality logs an error and returns `-EINVAL`.

Cleanup and defaults:
- `crypt_random_exit()` closes both descriptors and resets initialization.
- `crypt_random_default_key_rng()` maps build-time `DEFAULT_RNG` to `CRYPT_RNG_RANDOM` or `CRYPT_RNG_URANDOM`; any other value aborts.

Important details:
- `/dev/random` progress messages are user-visible and localized with `_()`.
- The file assumes `crypt_random_init()` has opened descriptors before `crypt_random_get()` is called.
- In FIPS mode, salt/key randomness delegates to `crypt_backend_rng()` with prediction resistance flag `1`.
