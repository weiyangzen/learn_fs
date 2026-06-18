<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/gpio/machine.h -->
# sources/distributed-fs/ceph-client/include/linux/gpio/machine.h

Purpose: This header declares the machine/board lookup table interface for mapping consumer device/function names to GPIO controller labels and line offsets on non-firmware or board-file platforms.

Important APIs/types/functions: `struct gpiod_lookup` records chip label, hardware index, connection id, index within a connection, lookup flags, and optional key/transitory flags. `GPIO_LOOKUP()` and `GPIO_LOOKUP_IDX()` build entries. `struct gpiod_lookup_table` associates a device id with a list of lookups. APIs include `gpiod_add_lookup_table()`, `gpiod_add_lookup_tables()`, `gpiod_remove_lookup_table()`, `gpiod_remove_lookup_tables()`, and managed variants. `struct gpiod_hog` and `GPIO_HOG()` describe boot-time/request-time hogged GPIOs.

Control flow, state, and persistence: Lookup tables are registered globally so later consumer lookups can resolve `(dev_id, con_id, idx)` to a chip line and flags. Device-managed APIs tie table lifetime to a parent device. Hog entries persist as requested lines until the provider or table is removed.

Dependencies/integration: It connects board data to gpiolib descriptors. It coexists with firmware-node mappings but is especially relevant for legacy platform data.

Risks and test signals: Static chip labels and offsets are fragile when providers move to dynamic GPIO bases; labels must match registered chips. Incorrect flags invert semantics or create open-drain/source mismatches. Tests should cover table add/remove ordering, duplicate entries, managed cleanup, hog direction/value setup, and consumer lookup by indexed connection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/gpio/machine.h -->
