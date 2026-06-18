# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/tlan.h

## Purpose
`tlan.h` defines the hardware constants, descriptor formats, private driver state, adapter flags, register offsets, interrupt codes, PHY/MII definitions, and inline I/O helpers used by the ThunderLAN driver in `tlan.c`.

It is the hardware contract for the driver: descriptor sizes, ring lengths, DIO access semantics, MII register definitions, EEPROM constants, and multicast hash calculation all live here.

## Important APIs, Types, And Macros
`struct tlan_adapter_entry` describes vendor/device IDs, labels, flags, and address offsets for adapter tables. The implementation uses a local `struct board` with similar fields, but the flags originate here: `TLAN_ADAPTER_UNMANAGED_PHY`, `TLAN_ADAPTER_BIT_RATE_PHY`, `TLAN_ADAPTER_USE_INTERN_10`, and `TLAN_ADAPTER_ACTIVITY_LED`.

Descriptor types are `struct tlan_buffer` and `struct tlan_list`. A list has a `forward` DMA pointer, `c_stat`, `frame_size`, and ten buffer descriptors. Ring sizing constants are `TLAN_NUM_RX_LISTS`, `TLAN_NUM_TX_LISTS`, `TLAN_BUFFERS_PER_LIST`, `TLAN_MIN_FRAME_SIZE`, and `TLAN_MAX_FRAME_SIZE`.

`struct tlan_priv` is the netdevice private state used by `tlan.c`. It stores netdev/PCI pointers, coherent descriptor storage, RX/TX descriptor and buffer DMA metadata, ring indexes, PHY status and timers, board metadata, module parameter selections, selected PHY addresses, ThunderLAN revision/full-duplex state, spinlock, and timeout work.

Register definitions cover EISA IDs/config registers, host registers (`TLAN_HOST_CMD`, `TLAN_CH_PARM`, `TLAN_DIO_ADR`, `TLAN_HOST_INT`, `TLAN_DIO_DATA`), internal DIO registers (`TLAN_NET_CMD`, `TLAN_NET_SIO`, `TLAN_NET_STS`, `TLAN_NET_MASK`, `TLAN_NET_CONFIG`, address/hash/stat registers, LED, max RX, interrupt disable), interrupt type values, generic MII registers, and ThunderLAN-specific PHY registers.

Inline helpers are `tlan_dio_read8()`, `tlan_dio_read16()`, `tlan_dio_read32()`, `tlan_dio_write8()`, `tlan_dio_write16()`, `tlan_dio_write32()`, `tlan_clear_bit()`, `tlan_get_bit()`, `tlan_set_bit()`, and `tlan_hash_func()`.

## Control Flow Role
The header does not implement the driver lifecycle, but its inline helpers define how all DIO register access works: write the internal register address to `base + TLAN_DIO_ADR`, then read or write the appropriately offset `TLAN_DIO_DATA` byte/word/dword lane. `tlan.c` uses this throughout reset, stats, multicast, MAC programming, PHY control, and LED handling.

Ring-control macros and bits drive TX/RX flow. `TLAN_CSTAT_READY`, `TLAN_CSTAT_FRM_CMP`, `TLAN_CSTAT_EOC`, `TLAN_CSTAT_UNUSED`, and `TLAN_LAST_BUFFER` are the status and buffer markers that the TX/RX interrupt handlers interpret. `CIRC_INC()` advances ring heads/tails with wraparound.

Timer constants identify the staged reset/link state machine used by `tlan_timer()`: activity LED, PHY power down/up, PHY reset, link start, autonegotiation finish, and final reset completion.

`tlan_hash_func()` maps a multicast Ethernet address to a six-bit ThunderLAN hash-table index. `tlan_set_multicast_list()` uses the first three multicast addresses in address registers and hashes the rest into `TLAN_HASH_1`/`TLAN_HASH_2`.

## State And Persistence Behavior
The header defines in-memory state layout but does not allocate it. `struct tlan_priv` persists for the life of an allocated netdevice. Descriptor lists point to DMA-coherent memory allocated by `tlan.c`; their status words are shared state between CPU and adapter hardware.

The many register constants correspond to volatile hardware state. EEPROM constants describe a 256-byte serial EEPROM read by the driver, but no write helpers are declared here.

## Dependencies And Integration Points
The header depends on Linux I/O, types, and netdevice headers. It is included by `tlan.c` and expects a `debug` variable in scope for `TLAN_DBG()`. It defines fallback PCI IDs for Olicom devices when generic PCI headers do not provide them.

The inline I/O helpers are tied to x86-style I/O port accessors (`inb/outb/inw/outw/inl/outl`) and ThunderLAN DIO address/data semantics. MII constants are duplicated locally rather than using only modern `linux/mii.h` names, reflecting the driver's legacy register programming style.

## Risks And Edge Cases
The header is dense with hardware magic values. Incorrect bit definitions affect reset, interrupts, PHY state, descriptor ownership, and stats accounting. `TLAN_DBG()` references a global `debug`, so it is not a generic reusable macro outside the driver implementation context.

The descriptor format reserves ten buffer slots, while `tlan.c` uses slots 8 and 9 to store SKB pointers. Any hardware interpretation of those slots, or a future descriptor format change, would break this convention. `tlan_dio_write32()` adds `(internal_addr & 0x2)` to `TLAN_DIO_DATA`, matching the existing driver behavior but requiring correct alignment assumptions.

`tlan_hash_func()` is optimized bit arithmetic for a specific six-bit hash. It must remain compatible with the hardware multicast hash table; substituting a standard CRC multicast hash would be wrong for this device.

## Test Signals
Compile tests should catch missing PCI ID definitions, structure layout issues, and access to `debug` from `TLAN_DBG()`. Runtime validation comes indirectly through `tlan.c`: DIO reads/writes should return expected revision and stats registers, descriptors should transition through READY/FRM_CMP/EOC states, MII register accesses should work for internal and external PHYs, multicast hash filtering should admit expected multicast traffic, and ring wraparound through `CIRC_INC()` should remain stable under traffic.
