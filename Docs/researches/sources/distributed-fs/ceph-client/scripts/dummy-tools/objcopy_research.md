# sources/distributed-fs/ceph-client/scripts/dummy-tools/objcopy

Purpose: Dummy `objcopy` shim for build/Kconfig probes.

Important APIs/functions: Uses `arg_contain()` and emits `GNU objcopy (scripts/dummy-tools/objcopy) 2.50` for version probes.

Control flow: Handles `--version`/`-v`; otherwise exits success without transforming files.

State/persistence: Stateless and does not create output files.

Dependencies/integration: Used by dummy cross-toolchain mode for capability discovery.

Risks: Any real build step requiring output files will fail later or consume stale files because this script does nothing.

Test signals: Version output and behavior when passed typical `objcopy` arguments by Kbuild probes.
