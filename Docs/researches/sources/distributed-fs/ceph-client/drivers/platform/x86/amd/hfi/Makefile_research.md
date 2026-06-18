# sources/distributed-fs/ceph-client/drivers/platform/x86/amd/hfi/Makefile

Purpose: this Makefile builds the AMD HFI driver.

Important APIs, types, and functions: it maps `CONFIG_AMD_HFI` to `amd_hfi.o` and composes that object from `hfi.o`.

Control flow: kbuild includes the object only when `AMD_HFI` is selected.

State and persistence: build-only state; no runtime behavior.

Dependencies and integration points: tied to `amd/hfi/Kconfig` and to the top-level AMD Makefile that descends into this directory.

Risks: object naming must stay aligned with the module/driver name. Since `AMD_HFI` is bool, the object is linked into vmlinux when enabled.

Test signals: build artifact inclusion and successful link of `hfi.o` into `amd_hfi.o`.
