# sources/distributed-fs/ceph-client/include/linux/atmdev.h

## Purpose
Defines core in-kernel ATM device and VCC structures, statistics, operations, socket accounting helpers, registration APIs, ioctl hooks, and notifier hooks.

## Important APIs, Types, And Functions
Statistics structures use atomic counters for AAL stats. VCC flags enumerate address, ready, partial, registered, bound, released, listen, meta, session, SAP, close, waiting, and CLIP states; `ATM_VF2VS()` maps flags to visible socket state. `struct atm_vcc` embeds `struct sock` first and stores VPI/VCI, options, device, QoS/SAP, callbacks (`push`, `pop`, `push_oam`, `send`, release), protocol/device data, stats, SVC addresses, session pointer, and user backlink. `struct atm_dev` stores ops, PHY ops, type/number, data, flags, address lists, ESI, CI range, stats, signal, link rate, refcount, lock, proc entry, class device, and list linkage. `struct atmdev_ops` and `struct atmphy_ops` declare driver callbacks. APIs include device register/lookup/deregister, signal change, VCC release, socket insertion, charging/allocation, PCR goal, async release, ioctl register/deregister, and device notifier register/unregister. Inline helpers convert socket types, account TX/RX memory, test send allowance, and hold/put devices.

## Control Flow, State, And Persistence
ATM runtime state is substantial: global VCC hash table and socket list lock, per-device refcounts and lists, per-VCC flags and callbacks, and socket memory accounting. `atm_dev_put()` closes devices only after removal is flagged and refcount reaches zero. TX accounting stores the skb truesize at charge time in `ATM_SKB(skb)` so later skb expansion does not corrupt accounting.

## Dependencies And Integration Points
Depends on wait queues, time, net/socket/skbuff/uio, atomic/refcount, UAPI ATM device definitions, procfs, and compat. Integrated by ATM core, device drivers, PHY drivers, CLIP/br2684, proc/sysfs, ioctl extension modules, and network notifier clients.

## Risks And Test Signals
Risks include refcount bugs, skb accounting imbalance, callback lifetime/module ownership, VCC flag races, and device removal while VCCs remain. Tests should cover device register/deregister, VCC open/close/send, signal notifier events, TX/RX accounting under skb resizing, ioctl extension handling, compat ioctls, proc entries, and refcount release assertions.
