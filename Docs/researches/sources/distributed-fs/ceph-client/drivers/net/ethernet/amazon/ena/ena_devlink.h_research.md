# sources/distributed-fs/ceph-client/drivers/net/ethernet/amazon/ena/ena_devlink.h

Purpose: this header declares ENA devlink lifecycle and parameter helpers and defines how to retrieve the ENA adapter pointer from devlink private storage.

Important APIs, types, and functions: `ENA_DEVLINK_PRIV(devlink)` casts `devlink_priv()` to a stored `struct ena_adapter *`. Declarations include `ena_devlink_alloc()`, `ena_devlink_free()`, `ena_devlink_register()`, `ena_devlink_unregister()`, `ena_devlink_params_get()`, and `ena_devlink_disable_phc_param()`.

Control flow: the header has no execution. ENA probe/remove and PHC paths call the declared functions to set up devlink, read the PHC parameter, and disable it when needed.

State and persistence: no state is defined here beyond the private-storage convention. The actual state is the devlink object, devlink port, and adapter pointer managed in `ena_devlink.c`.

Dependencies and integration points: it includes `ena_netdev.h` and `<net/devlink.h>`, tying devlink support to the ENA adapter structure and Linux devlink core.

Risks: the private macro assumes devlink was allocated with enough private storage for one adapter pointer; changing allocation size or type would break all users. Include coupling to `ena_netdev.h` can propagate devlink dependencies broadly.

Test signals: build/link tests should catch declaration drift. Runtime signals are successful devlink allocation/registration, parameter access, reload, and clean unregister/free during remove.
