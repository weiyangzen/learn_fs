# File Research: sources/block-storage/util-linux/libmount/src/hook_veritydev.c

This conditional hook implements dm-verity setup for mount options such as `verity.hashdevice=`, `verity.roothash=`, `verity.roothashfile=`, FEC settings, root-hash signatures, and corruption policy. It uses libcryptsetup directly or through `dlopen()`.

Key components:

- `struct hookset_data` stores the created mapper device path and optional dlopen handles/function pointers.
- `new_hookset_data()` loads libcryptsetup symbols when configured for dlopen, enables cryptsetup debug logging for verbose contexts, and installs a log callback.
- `is_veritydev_required()` checks userspace verity option flags for normal mounts.
- `setup_veritydev()` parses options, creates or reuses a dm-verity mapper device, and rewrites `cxt->fs` source to `/dev/mapper/<roothash>-verity`.
- `hook_mount_post()` deletes or defers deletion of the mapper device.

Important behavior:

- Verity mounts are forced read-only by appending `MS_RDONLY`.
- Mandatory inputs are a hash device plus either root hash or root hash file; root hash and root hash file are mutually exclusive.
- Hash/FEC offsets and roots are parsed as sizes; default FEC roots is `2`.
- `verity.roothashsig=` reads a non-empty regular file and activates by signed key when libcryptsetup supports it.
- `verity.oncorruption=` accepts `ignore`, `restart`, and optionally `panic` if the cryptsetup flag exists.
- The mapper device name is derived from the root hash to allow deduplication and reuse.
- If activation returns `-EEXIST`, the hook opens the existing mapper, extracts the current root hash where supported, compares it to the requested hash, and validates signed/unsigned consistency when signatures are supported.
- Successful setup changes mount source to the mapper device. Cleanup uses deferred deactivation when the mount succeeded.

Dependencies and interactions:

- Active only with `HAVE_CRYPTSETUP`.
- Uses libcryptsetup APIs, path reading helpers, userspace option maps, and mount status to decide deferred cleanup.

Risk notes:

- Device reuse is intentionally conservative; inability to verify an existing device's root hash is treated as `-EEXIST`.
- Root hash conversion requires even-length valid hex matching libcryptsetup's volume key size.
- When using `dlopen()`, missing symbols surface as user messages from `dlerror()`.
