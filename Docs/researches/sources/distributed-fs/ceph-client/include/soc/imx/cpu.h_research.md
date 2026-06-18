# sources/distributed-fs/ceph-client/include/soc/imx/cpu.h

Purpose: provides i.MX/Vybrid CPU type numeric identifiers and exposes the global detected CPU type.

Important APIs and types: macros define legacy MX1/MX2/MX3/MX5, i.MX6/i.MX7, and Vybrid CPU IDs, including composite VF510/VF610 values and a virtual i.MX6ULZ ID. Outside assembly, `extern unsigned int __mxc_cpu_type` provides the detected type.

Control flow: platform code sets `__mxc_cpu_type` during early SoC detection and drivers/board code compare it against these macros to select quirks or capabilities.

State and persistence: `__mxc_cpu_type` is runtime global kernel state initialized from hardware/boot data. It is not persistent.

Dependencies and integration points: assembly-safe macro header integrated by i.MX platform and driver quirk code.

Risks and test signals: risks include stale ID comparisons, duplicate/virtual IDs, and using CPU type where device tree compatibles would be safer. Test early SoC detection, quirk selection on each supported family, assembly include compatibility, and compile coverage for ARM i.MX/Vybrid configs.
