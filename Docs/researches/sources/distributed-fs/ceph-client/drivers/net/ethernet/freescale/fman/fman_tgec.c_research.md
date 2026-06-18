# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fman/fman_tgec.c

## Purpose
Implements the FMan 10 Gigabit Ethernet Controller (TGEC/XGEC) MAC backend. It provides register programming, phylink callbacks, multicast hash filtering, timestamp enable, exception handling, and the `tgec_initialization` hook used by the FMan MAC platform driver.

## Important APIs, Types, and Functions
Defines the TGEC register map `struct tgec_regs`, configuration `struct tgec_cfg`, and backend-private `struct fman_mac`. Key functions are `tgec_config`, `tgec_init`, `tgec_free`, `tgec_initialization`, `tgec_link_up`, `tgec_link_down`, `tgec_modify_mac_address`, `tgec_add_hash_mac_address`, `tgec_del_hash_mac_address`, `tgec_set_allmulti`, `tgec_set_promiscuous`, `tgec_set_tstamp`, `tgec_set_exception`, and interrupt callback `tgec_err_exception`.

## Control Flow and State
Initialization assigns function pointers into `struct mac_device`, converts legacy XGMII DT mode to XAUI, advertises 10G full-duplex and pause capabilities, allocates the private MAC/config objects, resets the MAC if enabled, writes station address/default config/max frame/pause/interrupt masks, allocates multicast and unicast hash tables, registers FMan MAC error interrupts, frees the transient config, and disables Tx ECC exceptions. Link-up configures pause, updates the parent MAC speed, and sets Rx/Tx enable bits; link-down clears them. Multicast filtering tracks software hash entries while programming TGEC hash-table control entries. Exception enable state is mirrored in `tgec->exceptions` and hardware `imask`.

## Dependencies and Integration Points
Depends on `mac.h`, `fman_mac.h`, FMan reset/interrupt/max-frame APIs, phylink, CRC/bit-reversal helpers, and shared FMan hash-table helpers. `mac.c` selects this backend for `fsl,fman-xgec` nodes; DPAA Ethernet later uses the installed `mac_device` operations for multicast, timestamp, promiscuous, and link control.

## Risks and Test Signals
Risks include multicast hash collisions/leaks, unicast hash requests being unsupported, endian-sensitive MAC address conversion, unsupported interface assumptions, exception mask drift, FMan revision errata handling, and freeing resources on partial initialization failures. Test signals include 10G XAUI link-up/down via phylink, multicast/allmulti/promiscuous filtering, timestamp bit toggling, FMan MAC interrupt delivery, max-frame programming, and error-path probe cleanup.
