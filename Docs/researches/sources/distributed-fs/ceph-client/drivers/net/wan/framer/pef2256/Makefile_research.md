# sources/distributed-fs/ceph-client/drivers/net/wan/framer/pef2256/Makefile

Purpose: kbuild rules for the Lantiq PEF2256 framer provider.

Important APIs, types, and functions: maps `CONFIG_FRAMER_PEF2256` to the module object `framer-pef2256.o`, built from `pef2256.o`.

Control flow: when the PEF2256 config is selected, this directory builds a single module/built-in object that registers the platform driver.

State and persistence: build-only file.

Dependencies and integration points: aligns the module name advertised by Kconfig with the object composition. The resulting driver depends on the generic framer framework, MFD, regmap MMIO, clocks, GPIO, and OF matching.

Risks: future split files must be added to `framer-pef2256-objs`; otherwise symbols will be missing. Module naming should remain consistent with Kconfig help and userspace expectations.

Test signals: verify module builds as `framer-pef2256` for `m` and links into vmlinux for `y`.
