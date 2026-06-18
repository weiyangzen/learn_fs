# sources/distributed-fs/ceph-client/drivers/nvmem/qcom-spmi-sdam.c

Purpose: Qualcomm SPMI SDAM NVMEM provider for small PMIC scratch/data memory.

Important APIs/types/functions: `struct sdam_chip` stores parent regmap, base, size, and embedded config. `sdam_is_valid()` allows memory window accesses and one-byte PBS trigger registers. `sdam_is_ro()` prevents writes over read-only ID/version/size registers. `sdam_read()`/`sdam_write()` use regmap bulk operations.

Control flow: probe obtains the parent's regmap, reads the child `reg` base from OF, reads `SDAM_SIZE`, computes bytes as `val * 32`, and registers byte-granular read/write NVMEM. Runtime access validates range and write permissions before issuing regmap operations.

State/persistence: SDAM data may persist according to PMIC behavior; the driver has no cache. PBS trigger registers are exposed as special one-byte valid offsets.

Dependencies/integration: platform driver for `qcom,spmi-sdam`; depends on parent SPMI/regmap device and legacy fixed OF NVMEM cells.

Risks: NVMEM config size is set to SDAM memory size only, while valid access also permits trigger offsets outside that range; generic NVMEM bounds may prevent external access to those trigger registers unless cells account for it. Writes to partially overlapping RO registers are rejected.

Test signals: invalid range rejection, RO write rejection, SDAM_SIZE-derived sizing, regmap read/write errors, and PBS trigger single-byte access.
