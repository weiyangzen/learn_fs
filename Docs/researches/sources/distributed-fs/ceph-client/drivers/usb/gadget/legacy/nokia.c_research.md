# sources/distributed-fs/ceph-client/drivers/usb/gadget/legacy/nokia.c

Purpose: legacy Nokia N900 PC-Suite composite gadget exposing two configurations with ACM, ECM, mass storage, and optional Phonet/OBEX functions.

Important APIs, types, and functions: `device_desc`, `nokia_config_500ma_driver`, and `nokia_config_100ma_driver` define the two advertised configurations. `fsg_mod_data` configures two removable non-stalling LUNs. `nokia_bind` allocates string IDs, checks alternate setting support, obtains function instances, prepares mass-storage common state, and registers both configurations. `nokia_bind_config` materializes optional and mandatory functions and records per-configuration function pointers for unbind. `nokia_unbind` releases all functions and instances.

Control flow: bind first handles strings and hardware capability, then optional Phonet and OBEX instances are best-effort while ACM, ECM, and mass storage are required. Each configuration receives its own function objects from shared instances. Optional functions are added first if available, followed by ACM, ECM, and storage. Failure paths remove any functions already added and drop references.

State and persistence: static globals track function instances and per-config function objects. Storage LUNs and inquiry strings are prepared at bind time. Configurations differ by bus/self-powered attributes and max power values. No persistent state is written.

Dependencies and integration points: depends on libcomposite, `u_serial`, `u_ether`, `u_phonet`, `u_ecm`, and `f_mass_storage`. It integrates with hosts expecting Nokia vendor/product IDs and PC-Suite style interface composition.

Risks: optional function handling creates many `IS_ERR_OR_NULL` paths, and errors can easily cause missing puts or stale per-config pointers. The driver requires `gadget_is_altset_supported`, limiting UDC compatibility. Reusing old Nokia IDs and fixed composition can confuse modern hosts if descriptors change.

Test signals: build with and without Phonet/OBEX support, enumerate both configurations, verify 500 mA and 100 mA attributes, test ACM, ECM, and both storage LUNs, switch configurations repeatedly, inject optional function acquisition failure, and unload after both configurations have been bound.
