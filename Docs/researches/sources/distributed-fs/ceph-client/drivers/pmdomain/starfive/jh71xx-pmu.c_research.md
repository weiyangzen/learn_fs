<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/starfive/jh71xx-pmu.c -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/starfive/jh71xx-pmu.c

## Purpose
StarFive JH71XX PMU generic power-domain driver. It supports both the main JH7110 PMU with software-encourage sequencing and the always-on syscon-style PMU switch for DPHY domains.

## Important APIs, Types, And Functions
- `struct jh71xx_domain_info` describes domain name, genpd flags, and status bit.
- `struct jh71xx_pmu_match_data` selects domain table, status register, optional IRQ parser, and state setter.
- `struct jh71xx_pmu` owns device, match data, MMIO base, onecell data, IRQ, and spinlock.
- `struct jh71xx_pmu_dev` wraps a domain descriptor and genpd.
- Core functions include `jh71xx_pmu_get_state()`, `jh7110_pmu_set_state()`, `jh7110_aon_pmu_set_state()`, `jh71xx_pmu_set_state()`, `jh71xx_pmu_on/off()`, `jh71xx_pmu_interrupt()`, `jh7110_pmu_parse_irq()`, `jh71xx_pmu_init_domain()`, and `jh71xx_pmu_probe()`.

## Control Flow
The builtin platform driver matches `starfive,jh7110-pmu` or `starfive,jh7110-aon-syscon`, maps registers, initializes the spinlock, optionally requests and enables PMU interrupts, allocates onecell domain storage, and initializes each domain from match data. Main PMU transitions write the turn-on or turn-off mask, then issue the three-step SW encourage command sequence and poll `CURR_POWER_MODE` until the bit reaches the requested state. AON PMU transitions directly set or clear the switch register under the spinlock. Each genpd is initialized as off if the current state bit is not set.

## State And Persistence Behavior
Per-controller state includes MMIO base, domain array, IRQ, and lock. Per-domain state is descriptor pointer and genpd. Hardware status registers are the source of truth for current power mode. Interrupt status is logged and cleared but does not drive genpd state transitions.

## Dependencies And Integration Points
Depends on StarFive dt-bindings for domain indices, platform MMIO resources, optional IRQ, generic PM domains, and DT compatibles. Consumers bind through the onecell provider.

## Risks
SW encourage sequencing is strict; wrong command order or missing lock could corrupt PMU state. Poll timeout is only 100 us, so slow hardware or clocking issues show as `-ETIMEDOUT`. The IRQ parser enables all interrupts except P-channel failure but returns success even if `devm_request_irq()` fails after logging, because it does not return `ret`; that may hide IRQ setup failures.

## Test Signals
Boot should register all JH7110 main and AON domains. Runtime PM should toggle GPU/VDEC/VOUT/ISP/VENC/DPHY domains and see status bits change within timeout. Interrupt tests should verify sequence-done and failure status are logged and cleared.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/starfive/jh71xx-pmu.c -->
