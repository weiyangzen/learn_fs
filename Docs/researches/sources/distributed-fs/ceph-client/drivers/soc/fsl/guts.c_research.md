# sources/distributed-fs/ceph-client/drivers/soc/fsl/guts.c

Purpose: Freescale/NXP QorIQ Global Utilities driver for SoC identification. It reads the System Version Register, matches known die families, optionally reads a unique SoC ID from SFP, and registers SoC bus metadata.

Important APIs and functions: `fsl_guts_init()` is a `core_initcall`; `fsl_soc_die_match()` maps SVR masks to die names; `fsl_guts_get_soc_uid()` maps an SFP node and reads a 64-bit UID. Tables include many PowerPC and Layerscape ARM-compatible GUTS/DCFG nodes plus LS1028A SFP data.

Control flow: init finds the first matching GUTS/DCFG node, maps it, reads SVR in little or big endian based on DT property, allocates `soc_device_attribute`, fills machine/family/soc_id/revision/serial_number, registers the SoC device, and logs machine/family/revision. Allocation failures unwind allocated strings.

State and persistence: persistent state is the registered SoC device. No long-lived MMIO mapping remains after reading SVR/UID.

Dependencies and integration: depends on OF, `struct ccsr_guts` layout, SoC bus, optional SFP compatible nodes, and callers such as DPIO stashing logic that use `soc_device_match()` on family strings.

Risks and test signals: risks include matching only the first GUTS node, endian property mistakes, SVR mask table gaps, and serial number allocation failure after otherwise valid metadata. Test signals are `/sys/devices/soc0` contents, boot logs, DPIO SoC matching, LS1028A serial number presence, and clean no-op on non-QorIQ systems.
