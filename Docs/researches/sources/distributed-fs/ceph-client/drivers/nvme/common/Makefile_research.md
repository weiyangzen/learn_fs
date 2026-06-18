# sources/distributed-fs/ceph-client/drivers/nvme/common/Makefile

Purpose: Builds common NVMe authentication and keyring modules plus optional authentication KUnit tests.

Important APIs and flow: Adds `-I$(src)`, builds `nvme-auth.o` from `auth.o` under `CONFIG_NVME_AUTH`, builds `nvme-keyring.o` from `keyring.o` under `CONFIG_NVME_KEYRING`, and includes `tests/auth_kunit.o` under `CONFIG_NVME_AUTH_KUNIT_TEST`.

State and persistence behavior: Build-time only; no runtime state.

Dependencies and integration points: Ties Kconfig symbols to the common C implementations used by host and transport code.

Risks and test signals: Build matrix should cover auth without keyring, keyring without auth, built-in versus module, and KUnit test linkage.
