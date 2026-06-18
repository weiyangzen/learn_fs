# sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-periph-gate.c

Implements shared gate operations for Tegra peripheral clocks, including duplicate-clock reference counting, APB flush handling, reset-state enabled checks, and a hardware workaround.

`clk_periph_is_enabled()` checks enable bits and, unless `TEGRA_PERIPH_NO_RESET`, reset bits. Enable/disable paths hold a global spinlock and update an `enable_refcnt[clk_num]` array so duplicated clock definitions do not fight over one gate. First enable writes the enable-set register and optionally executes workaround `TEGRA_PERIPH_WAR_1005168`; final disable may read chip ID first for APB peripherals, then writes enable-clear. `disable_unused` disables only when the shared refcount is zero. `tegra_clk_register_periph_gate()` allocates a gate clock and stores bank metadata.

Hardware state persists in CAR enable/reset registers. Software state persists in the shared enable-refcount array supplied by the caller. The file depends on Tegra register-bank metadata, `tegra_read_chipid()` for APB flush, CCF gate ops, and SoC peripheral tables that share `periph_clk_enb_refcnt`.

Refcount mismatches can leave clocks stuck on or off; the code warns on disabling an unenabled clock. Duplicated critical clocks rely on `disable_unused` behavior. Test signals include duplicate gate users, APB peripheral disable safety, reset-aware enable state, and workaround execution on affected clocks.
