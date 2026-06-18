# sources/distributed-fs/ceph-client/drivers/platform/x86/dell/alienware-wmi.h

Purpose: Shared internal interface for the composite Alienware WMI driver.

Important APIs/types/functions: Defines GUIDs, interface/control-state enums, `struct alienfx_quirks`, packed `struct color_platform`, `struct alienfx_priv`, `struct alienfx_ops`, and `struct alienfx_platdata`. Declares shared globals and setup/command helpers.

Control flow/state/persistence: Header-only. Conditional stubs return `-ENODEV` when legacy or WMAX subdrivers are disabled; `WMAX_DEV_GROUPS` conditionally extends platform sysfs groups.

Dependencies/integration: Connects base, legacy, and WMAX files and includes LED/platform/WMI types.

Risks/test signals: Packed argument layouts and conditional compilation are the main concerns. Build-test all legacy/WMAX enabled and disabled combinations.
