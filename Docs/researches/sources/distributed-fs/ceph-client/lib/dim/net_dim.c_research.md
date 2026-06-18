# sources/distributed-fs/ceph-client/lib/dim/net_dim.c

## Purpose
Implements network Dynamic Interrupt Moderation profiles, profile storage on `struct net_device`, and the network DIM tuning algorithm.

## APIs, Types, and Functions
Exports profile accessors `net_dim_get_rx_moderation()`, `net_dim_get_def_rx_moderation()`, `net_dim_get_tx_moderation()`, and `net_dim_get_def_tx_moderation()`. Device integration APIs are `net_dim_init_irq_moder()`, `net_dim_free_irq_moder()`, `net_dim_setting()`, `net_dim_work_cancel()`, `net_dim_get_rx_irq_moder()`, `net_dim_get_tx_irq_moder()`, `net_dim_set_rx_mode()`, `net_dim_set_tx_mode()`, and main algorithm `net_dim()`. Static profile tables provide RX/TX EQE and CQE moderation values.

## Control Flow
Initialization allocates `dev->irq_moder`, copies default RX/TX profiles based on flags and modes, stores work callbacks, and publishes profile pointers with RCU. Freeing clears RCU pointers and releases profile copies after grace periods. `net_dim_setting()` initializes a `struct dim` work item and mode for RX or TX. `net_dim()` collects event deltas until `DIM_NEVENTS`, computes stats, compares byte rate first, packet rate second, and event rate inversely, then steps left/right, turns, parks on top, or parks tired. When the profile index changes it sets `DIM_APPLY_NEW_PROFILE` and schedules driver work.

## State and Persistence
Persistent state lives in `dev->irq_moder` profile copies, mode fields, coal/profile flags, work callbacks, and caller-owned `struct dim` tuning state. RCU protects profile pointer replacement/free. No module-global mutable state is used beyond static profile templates.

## Dependencies and Integration Points
Depends on `<linux/dim.h>`, `<linux/rtnetlink.h>`, RCU, workqueues, netdevice storage, and driver-supplied DIM work callbacks that actually apply the selected moderation values. It integrates with NIC RX/TX completion paths and ethtool-like coalescing configuration.

## Risks and Test Signals
Risks include invalid profile mode/index, missing RTNL when freeing, RCU misuse, scheduling work after teardown, unstable tuning under noisy traffic, and dereferencing `dev->irq_moder` when not initialized. Test signals include NIC driver DIM tests, RCU/KASAN teardown tests, profile mode switching, synthetic traffic ramps, work cancellation on device close, and lockdep checks around RTNL assumptions.
