# sources/distributed-fs/ceph-client/drivers/net/ethernet/emulex/Kconfig

Purpose: defines the top-level Kconfig menu switch for Emulex Ethernet devices under the kernel networking drivers tree and includes the be2net-specific Kconfig when the vendor menu is enabled.

Important APIs/types/functions: `config NET_VENDOR_EMULEX` is a boolean menu option titled "Emulex devices"; it defaults to `y`, depends on `PCI`, and gates the nested `source "drivers/net/ethernet/emulex/benet/Kconfig"` inside `if NET_VENDOR_EMULEX`.

Control flow: Kconfig evaluation first checks PCI availability. If `NET_VENDOR_EMULEX=n`, all Emulex-specific driver prompts below this file are skipped. If enabled, the `benet/Kconfig` file contributes `BE2NET` and related chipset/HWMON options to the configuration UI.

State and persistence behavior: no runtime state. The selected boolean is persisted only in the kernel `.config` and controls which downstream symbols are visible and buildable.

Dependencies/integration points: integrates with the kernel Kconfig hierarchy and the `drivers/net/ethernet/emulex/Makefile`, where `CONFIG_BE2NET` later selects the `benet/` build directory. The dependency on `PCI` matches the hardware bus used by supported Emulex adapters.

Risks: disabling this vendor symbol hides be2net even if a user expects to select a specific card. The default `y` keeps prompts visible in PCI builds, but build output still depends on downstream tristate choices. The `source` path must remain aligned with the source tree location.

Test signals: run kernel configuration generation with `PCI=y` and `PCI=n`, verify `NET_VENDOR_EMULEX=n` hides `BE2NET`, verify `NET_VENDOR_EMULEX=y` exposes `benet/Kconfig`, and confirm `.config` plus Makefile produce or omit `drivers/net/ethernet/emulex/benet/` as expected.
