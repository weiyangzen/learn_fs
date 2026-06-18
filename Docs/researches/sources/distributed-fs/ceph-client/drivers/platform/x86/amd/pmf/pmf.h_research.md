# sources/distributed-fs/ceph-client/drivers/platform/x86/amd/pmf/pmf.h

Purpose: `pmf.h` is the shared PMF contract across core, ACPI, static slider, Auto Mode, CnQF, Smart PC, TEE, and SPC layers.

Important APIs, types, and functions: it defines policy buffer limits, APMF function IDs, SMU message IDs, platform profile slider constants, PMF policy action IDs, TA UUIDs, APMF/SBIOS request structures, SMU metrics v1/v2 structures, power source/mode enums, `struct amd_pmf_dev`, static-slider structures, auto-mode and CnQF configuration structures, Smart PC condition/action/TA shared-memory structures, and cross-file prototypes.

Control flow: not executable, but it defines the data flow: ACPI fills APMF structures, core stores them in `amd_pmf_dev`, metrics/feature engines consume them, Smart PC populates TA enact inputs, TEE returns policy actions, and core/feature layers apply SMU/ACPI outputs.

State and persistence: `struct amd_pmf_dev` centralizes runtime state including MMIO mapping, metrics buffers, delayed works, locks, debugfs, platform profile device, Smart PC policy buffer/TEE session/shared memory, ACPI request snapshots, custom BIOS input ring, and feature flags. No state is instantiated in the header.

Dependencies and integration points: includes ACPI, AMD PMF I/O UAPI, circular buffer helpers, input, platform device, and platform profile. It exposes `amd_pmf_get_npu_data()` indirectly through core source and declares namespace-shared PMF functions.

Risks: duplicated declaration of `amd_pmf_source_as_str()` suggests header drift. Many packed firmware structures require exact layout with ACPI/TEE/SBIOS contracts; changes can break firmware ABI. The central device struct creates tight coupling and makes partial feature builds hard, reflected by broad Kconfig dependencies.

Test signals: compile all PMF objects with this header, validate packed struct sizes against firmware expectations, exercise PMF IF v1/v2 paths, Smart PC custom BIOS input mapping, metrics v1/v2 CPU selection, and namespace consumers of exported PMF APIs.
