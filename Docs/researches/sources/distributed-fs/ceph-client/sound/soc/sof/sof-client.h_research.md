# sources/distributed-fs/ceph-client/sound/soc/sof/sof-client.h

Purpose: public header for SOF auxiliary client drivers. It defines the client device wrapper, conversion macros, IPC helper APIs, DSP/firmware accessors, and notification registration types.

Important APIs/types: `struct sof_client_dev` embeds `struct auxiliary_device` and a client-private `data` pointer. Macros convert auxiliary devices or devices back to `sof_client_dev`. IPC APIs include transmit with optional reply, no-reply inline helper, set/get data, and IPC3 receive injection. IPC4-specific helpers locate firmware modules and widgets by ID. Accessors return debugfs root, DMA device, firmware version, IPC max payload, IPC type, and firmware state. `sof_client_boot_dsp()` requests firmware boot, and `sof_client_core_module_get()/put()` protect the parent SOF module. Callback typedefs and registration functions expose IPC notification and firmware-state subscriptions.

Control flow/state: this header only declares operations; the caller owns callback lifetime and must unregister before its auxiliary driver/device disappears. `cdev->data` is the main persistence hook for client-specific runtime state.

Dependencies/integration: depends on auxiliary bus, Linux device/list types, and SOF public enums. It is consumed by probe/debug client modules and platform clients that need controlled access to the SOF core.

Risks/test signals: clients must respect IPC-type constraints and should not assume IPC4 helpers exist in non-IPC4 builds unless Kconfig selects the needed symbols. Notification callback concurrency depends on the implementation in `sof-client.c`; client tests should unregister handlers during remove and verify no callbacks arrive after teardown.
