<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/misc/md5.h -->
# sources/distributed-fs/orangefs/src/common/misc/md5.h

Purpose: declares the standalone MD5 streaming API and state layout used by `md5.c`.

Important types: `md5_byte_t` is an 8-bit byte type; `md5_word_t` is an unsigned 32-bit word by convention; `md5_state_t` stores the 64-bit bit count as two words, four digest words, and a 64-byte partial block buffer.

Important APIs: `md5_init(md5_state_t *pms)`, `md5_append(md5_state_t *pms, const md5_byte_t *data, int nbytes)`, and `md5_finish(md5_state_t *pms, md5_byte_t digest[16])`. The header supports C++ callers with `extern "C"`.

State behavior: callers allocate and own `md5_state_t`, append input bytes, and receive a 16-byte digest. After finish, the state has been mutated by padding and should be reinitialized before reuse.

Dependencies are minimal and intentionally standalone. Integration in this subset is `dist-dir-utils.c`, which hashes directory entry names and takes part of the digest for bucket placement.

Risks: `md5_word_t` assumes `unsigned int` is 32 bits. The API accepts `int` length rather than `size_t`. Security-sensitive callers should not use this API for authentication or collision resistance. Tests should check C and C++ inclusion, digest vector compatibility, and platform word-size assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/misc/md5.h -->
