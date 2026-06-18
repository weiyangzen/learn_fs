# sources/distributed-fs/ceph-client/sound/soc/sof/amd/Makefile

Purpose: AMD SOF object composition for common ACP code and per-platform PCI/DAI modules.

Important APIs/types/functions: `snd-sof-amd-acp-y` contains `acp.o`, loader, IPC, PCM, stream, trace, and common ops files. `acp-probes.o` is conditional. Per-platform modules pair PCI glue with platform DAI ops (`pci-rn.o` plus `renoir.o`, etc.).

Control flow: each Kconfig symbol emits its corresponding module through `obj-*`. Common support is shared by all platform modules.

State and persistence: build-time only.

Dependencies and integration points: maps AMD Kconfig selections to the source files researched here. Common ACP symbols are exported in the `SND_SOC_SOF_AMD_COMMON` namespace and imported by per-platform modules.

Risks: a platform module depends on both its PCI file and ops-init file being linked together; mismatches would fail probe-time ops initialization or symbol resolution.

Test signals: build coverage for all AMD platform configs and module namespace import checks.
