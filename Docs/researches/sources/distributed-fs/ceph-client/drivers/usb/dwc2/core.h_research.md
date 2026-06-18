<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/dwc2/core.h -->
# sources/distributed-fs/ceph-client/drivers/usb/dwc2/core.h

## Purpose
`core.h` is the shared internal contract for the DWC2 driver. It defines the central `struct dwc2_hsotg` state object, endpoint/request structures, parameter and hardware capability structures, register backup layouts, host scheduler constants, low-power and EP0 state enums, MMIO helpers, compile-time host/gadget stubs, and prototypes for common, host, gadget, DRD, debug, platform, and parameter code.

## Important APIs, types, and functions
Important types include `dwc2_hsotg_ep`, `dwc2_hsotg_req`, `dwc2_lx_state`, `dwc2_ep0_state`, `dwc2_core_params`, `dwc2_hw_params`, `dwc2_gregs_backup`, `dwc2_dregs_backup`, `dwc2_hregs_backup`, `dwc2_hsotg`, and `dwc2_halt_status`. Important helpers are `dwc2_readl`, `dwc2_writel`, `dwc2_readl_rep`, `dwc2_writel_rep`, `dwc2_is_iot`, `dwc2_is_fs_iot`, `dwc2_is_hs_iot`, `dwc2_is_host_mode`, `dwc2_is_device_mode`, and `call_gadget`. The header also declares the common reset/power/PHY/interrupt functions and conditional host/gadget APIs.

## Control flow
The header encodes compile-time control flow with `IS_ENABLED(CONFIG_USB_DWC2_HOST)`, `CONFIG_USB_DWC2_PERIPHERAL`, and dual-role checks. When a mode is not built, inline stubs make common code compile while returning harmless defaults. `call_gadget` releases and reacquires the controller spinlock around gadget driver callbacks to avoid callback execution under the DWC2 lock. MMIO helpers centralize optional byte swapping before every register access.

## State and persistence behavior
`struct dwc2_hsotg` is the persistent in-memory controller state across interrupts, role changes, suspend/resume, host scheduling, gadget endpoint operations, debugfs, and platform resources. It stores hardware-derived parameters, selected parameters, requested dual-role mode, role switch handle/default, low-level hardware flags, hibernation/partial-power-down flags, bus suspend state, PHY/clocks/resets/regulators, the global spinlock, OTG workqueue/timer, register backups, host schedule lists and bitmaps, DMA buffers and caches, gadget endpoint arrays, EP0 buffers, test mode, FIFO map, and connection/enabled flags.

## Dependencies and integration points
The header integrates with Linux PHY, regulator, USB gadget, USB OTG, USB role, debugfs, HCD, platform, ACPI/OF matching, and DWC2 register definitions in `hw.h`. It is included by nearly every DWC2 source file and is therefore the main boundary between platform setup, common core, host controller, gadget controller, DRD role switching, interrupts, and debugfs.

## Risks
Because `dwc2_hsotg` is large and mode-dependent, adding fields or changing conditionals can break ABI expectations inside the driver or create uninitialized state in one mode. The no-op stubs can conceal missing feature behavior in unsupported builds. MMIO byte swapping must be correct for every register access. Locking assumptions around `call_gadget` are subtle because callbacks run with the spinlock dropped and shared state may change.

## Test signals
Compile matrices across host-only, peripheral-only, dual-role, debugfs, and missed-SOF tracking are critical. Runtime signals include lockdep coverage around gadget callbacks, sparse or Coccinelle checks for MMIO accessor usage, suspend/resume verifying backup structures, host periodic scheduling tests, endpoint queue debugfs visibility, and role-switch tests ensuring fields present only in some configurations are not accessed in others.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/dwc2/core.h -->
