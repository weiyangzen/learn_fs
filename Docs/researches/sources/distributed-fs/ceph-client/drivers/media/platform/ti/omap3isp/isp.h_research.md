# sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap3isp/isp.h


Purpose: Defines the OMAP3 ISP core data model, register access helpers, resource enums, exported core APIs, and the aggregate `struct isp_device` shared by all ISP submodules.

Important APIs/types: Enums define MMIO resource indexes, SBL resources, subclock resources, xclk IDs, and revision/PHY constants. `struct isp_res_mapping` maps hardware revision to block offsets and PHY type. `struct isp_reg` supports context save/restore lists. `struct isp_xclk` represents an ISP-provided external clock. `struct isp_device` aggregates media/V4L2/notifier state, device resources, MMIO bases, syscon, IOMMU mapping, locks, crash/stop flags, refcount, clocks, xclks, CCDC/preview/resizer/CSI/CCP2/stat submodules, and resource bitmasks. `struct isp_async_subdev` stores async notifier connection plus bus config. Inline register helpers wrap raw read/write/clear/set/clear-set operations. Public functions cover flush, histogram DMA synchronization, module/pipeline stream control, bridge config, get/put, SBL/subclock resources, and entity registration.

Control flow: Included by nearly every OMAP3 ISP module. Submodules use `to_isp_device()` to recover the core, register helpers to access their MMIO windows, and exported functions to manage shared clocks/SBL/pipeline operations.

State and persistence: Declares all shared runtime state but stores none itself. Context persistence is volatile hardware-context save/restore managed by `isp.c`.

Dependencies/integration: Pulls in media entity, V4L2 async/device, clk provider, platform/device/wait headers, public `omap3isp.h`, and all internal submodule headers. This creates a central include hub for the driver.

Risks and test signals: Header coupling is high; changing `struct isp_device` or enum order can break every submodule and resource map. Raw MMIO helpers do not add barriers beyond raw access semantics, so callers must flush where required. Test full driver build after any signature/resource changes and exercise modules that use each MMIO range and subclock/SBL bit.
