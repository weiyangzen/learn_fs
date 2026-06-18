# sources/distributed-fs/ceph-client/arch/powerpc/platforms/8xx/micropatch.c

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/8xx/micropatch.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/8xx/micropatch.c

### Purpose
CPM1 microcode patch loader for selected MPC8xx variants and errata/workload support. It writes predefined patch words and parameter changes into CPM microcode/dual-port memory during CPM reset.

### Important APIs, Types, And Functions
Defines `struct patch_params`, variant-specific `patch_params` and patch arrays under configuration/CPU conditionals, helper `cpm_write_patch()`, and public `cpm_load_patch(cpm8xx_t *cp)`. It may adjust SPI parameter RAM (`struct spi_pram`) and CPM command/register fields after loading.

### Control Flow
When `CONFIG_UCODE_PATCH` is enabled, `cpm_reset()` calls `cpm_load_patch()`. The loader selects the compiled patch parameters, writes patch words to CPM memory offsets, updates relocation vectors/parameters, and performs any protocol-specific parameter RAM initialization.

### State, Persistence, And Dependencies
State is CPM internal microcode RAM and parameter RAM for the current boot. No filesystem persistence. Dependencies include CPM1 register layout, compiled microcode arrays, CPU/board configuration, and `cpm8xx_t`.

### Integration Points
Feeds the CPM runtime used by SCC/SMC/FEC/SPI and other communication drivers after reset.

### Risks
Very high hardware-specific risk: wrong offsets, CPU variant, or endianness can break CPM peripherals broadly. Patch selection must match silicon and config.

### Test Signals
Boot with patch-enabled configs, verify CPM serial/Ethernet/SPI operation, inspect patch-specific errata behavior, and build all conditional variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/8xx/micropatch.c -->
