# File Research: sources/cow-pools/bcachefs-tools/c_src/crypto.c

- Userspace crypto/passphrase support for bcachefs tools.
- Reads passphrases from terminal with echo disabled or from stdin.
- Derives passphrase keys using libsodium scrypt parameters stored in the superblock crypt field.
- Checks encrypted superblock keys by decrypting with chacha20 and testing key magic.
- Adds derived passphrase keys to Linux keyrings with `bcachefs:<uuid>` descriptions.
- Initializes and updates encrypted superblock keys, defaulting new encryption params to scrypt N=16384, R=8, P=16.
- Explicitly zeros sensitive temporary data.
