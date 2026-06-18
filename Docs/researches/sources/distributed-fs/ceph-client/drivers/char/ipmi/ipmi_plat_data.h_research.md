# sources/distributed-fs/ceph-client/drivers/char/ipmi/ipmi_plat_data.h

Purpose: This header defines the small platform-data contract used to synthesize IPMI platform devices from hardcoded, hotmod, and discovery paths.

Important APIs, types, and functions: `enum ipmi_plat_interface_type` distinguishes SI and SSIF platform devices. `struct ipmi_plat_data` carries interface type, SI type or SSIF marker, address space or SSIF interface number, base address, register spacing/size/shift, IRQ, slave address, and address-source metadata. `ipmi_platform_add` is declared as the constructor for such platform devices.

Control flow: The header has no executable flow. Its fields are consumed by `ipmi_platform_add`, then by platform probe paths that parse resources and software-node properties.

State and persistence behavior: The structure is caller-owned transient data. The long-lived state is created only after `ipmi_platform_add` copies fields into platform resources and device properties.

Dependencies and integration points: It includes `linux/ipmi.h` for `enum ipmi_addr_src`. It is shared by `ipmi_plat_data.c`, SI hardcode/hotmod helpers, and any platform-discovery code that fabricates IPMI devices.

Risks and edge cases: The comment-level field overloading is important: `type` and `space` mean different things for SI versus SSIF. Callers must zero-initialize the structure when leaving optional fields unset, because defaulting is done by the implementation. Bad address-source or register metadata can propagate into sysfs and duplicate-detection decisions.

Test signals: Compile-time users should cover both `IPMI_PLAT_IF_SI` and `IPMI_PLAT_IF_SSIF`, zero/defaulted register metadata, slave address propagation, and address-source propagation into created device properties.
