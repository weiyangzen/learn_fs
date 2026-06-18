# sources/distributed-fs/ceph-client/arch/mips/dec/prom/dectypes.h

Purpose: defines DEC PROM system-type numeric constants used during machine identification.

Important definitions: constants map DEC system IDs such as `DS2100_3100`, `DS5000_200`, `DS5000_1XX`, `DS5000_2X0`, `DS5800`, `DS5400`, `DS5000_XX`, `DS5500`, and `DS5100`.

Integration: consumed by `identify.c` to translate PROM `systype` values into Linux `mips_machtype` and model-specific initialization.

Risks and test signals: incorrect numeric mapping misidentifies the entire platform. Test by booting or emulating known PROM IDs and checking reported system type.
