# sources/distributed-fs/ceph-client/drivers/dma/qcom/hidma_mgmt_sys.c

Purpose: sysfs support for the HIDMA management driver. It exposes global management parameters and per-channel arbitration knobs, and reprograms hardware through `hidma_mgmt_setup` when writable values change.

Important APIs/types/functions: `struct hidma_chan_attr` wraps a per-channel kobject attribute with channel index and management pointer. `struct hidma_mgmt_fileinfo` maps global sysfs names to generated get/set functions. Macros `IMPLEMENT_GETSET` and `DECLARE_ATTRIBUTE` create common attribute handlers. Key functions are `show_values`, `set_values`, `show_values_channel`, `set_values_channel`, `create_sysfs_entry`, `create_sysfs_entry_channel`, and exported `hidma_mgmt_init_sys`.

Control flow: `hidma_mgmt_init_sys` allocates `chroots`, creates a `chanops` kobject under the device, creates `chanN` children for all channels, installs global files for revision/channel/limit values, and installs writable `priority` and `weight` files under each channel. Global setters parse an integer, locate the fileinfo entry, update the field, call `hidma_mgmt_setup`, and roll back on failure. Per-channel setters do the same for indexed priority/weight.

State/persistence: sysfs state is represented by devm-allocated attributes and kobjects. Values live in `hidma_mgmt_dev`; hardware is updated immediately on successful writes. There is no explicit remove function in this file, relying on device/kobject lifetime patterns.

Dependencies/integration: depends on `hidma_mgmt.c` for validation/programming and platform device drvdata. Uses sysfs/kobject APIs and standard numeric parsing.

Risks: kobject cleanup is not explicit in this file, so removal behavior should be checked against the wider driver lifecycle. Many global attributes are mode `S_IRUGO`, yet their fileinfo includes setters; permission bits rather than handler absence enforce read-only behavior. Concurrent sysfs writes can call full hardware setup repeatedly.

Test signals: sysfs tree creation for every channel, read all global files, write valid/invalid priority and weight values, verify rollback on invalid setup, and unbind/rebind under sysfs leak detection.
