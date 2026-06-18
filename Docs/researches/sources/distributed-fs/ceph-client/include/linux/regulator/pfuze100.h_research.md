# sources/distributed-fs/ceph-client/include/linux/regulator/pfuze100.h

Purpose: this header defines regulator ID numbers for Freescale/NXP PFUZE100-family PMIC variants. It lets board data, device-tree translation, and the PFUZE regulator driver agree on stable rail indexes.

Important APIs/types/functions: no functions or structs are declared. The exported surface is macro IDs for `PFUZE100_*`, `PFUZE200_*`, `PFUZE3000_*`, and `PFUZE3001_*` rails, plus `PFUZE100_MAX_REGULATOR`. IDs cover switching regulators, boost, SNVS/reference rails, VGEN/VLDO rails, coin-cell charger, VCCSD, and V33 rails depending on model.

Control flow: probe code selects a chip variant, builds regulator descriptors in the order declared here, and maps consumer constraints to these numeric IDs. Runtime control flow lives in the driver and regulator core; this header is a compile-time ABI between the driver and platform descriptions.

State and persistence: no runtime state. The only persistence concern is ID stability because existing device-tree bindings and platform data may rely on the numbering.

Dependencies and integration points: integrates with `drivers/regulator/pfuze100-regulator.c`, regulator init data, device-tree regulator nodes, and i.MX platform power trees.

Risks: changing values or reusing names for a different rail would silently bind constraints to the wrong output. Variant-specific omissions are easy to mishandle because PFUZE200/3000/3001 do not match PFUZE100 one-for-one. Test signals are successful regulator registration counts per variant, DT binding tests, rail-name/sysfs/regulator debugfs consistency, and boot validation on PFUZE-backed boards.
