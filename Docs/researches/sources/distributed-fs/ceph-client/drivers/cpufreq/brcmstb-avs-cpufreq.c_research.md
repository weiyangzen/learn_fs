# sources/distributed-fs/ceph-client/drivers/cpufreq/brcmstb-avs-cpufreq.c

## Purpose

This Broadcom STB driver exposes AVS firmware-controlled DFS/DVFS to cpufreq. The firmware running on a co-processor owns voltage and frequency changes; the Linux driver serializes mailbox commands, discovers supported P-states, and reports AVS status through cpufreq attributes.

## Important APIs, types, and functions

`struct private_data` stores mailbox MMIO, interrupt MMIO, completion, semaphore, saved PMAP, device pointer, and host IRQ. `struct pmap` represents firmware mode and PLL mapping parameters. The command core is `__issue_avs_command()`, with wrappers for PMAP and P-state get/set. Discovery and lifecycle helpers include `brcm_avs_is_firmware_loaded()`, `brcm_avs_get_freq_table()`, `brcm_avs_prepare_init()`, `brcm_avs_prepare_uninit()`, `brcm_avs_cpufreq_init()`, `brcm_avs_suspend()`, and `brcm_avs_resume()`.

## Control flow, state, and persistence

Probe maps the AVS CPU data and interrupt register regions, requests the optional host interrupt, verifies firmware magic and command support, stores the platform device in `brcm_avs_driver.driver_data`, and registers cpufreq. Policy init builds the frequency table by saving the current P-state, iterating P0 through P4, setting each P-state, reading back mailbox frequency, restoring the original P-state, enabling AVS, and setting `policy->cur`. Runtime target calls set a firmware P-state. Suspend saves PMAP and current P-state then sends S2 enter; resume sends S2 exit and restores PMAP, tolerating already-set maps. The semaphore serializes mailbox access, while completion or polling waits for firmware command completion.

## Dependencies and integration points

The driver depends on device-tree compatible regions `brcm,avs-cpu-data-mem` and `brcm,avs-cpu-l2-intr`, a named `sw_intr` interrupt when available, MMIO mailbox protocol, cpufreq generic table verification, and firmware support for AVS DVFS commands. It exports read-only cpufreq attributes for pstate, mode, pmap, voltage, and frequency.

## Risks and test signals

Risks include mailbox timeout handling, accidental out-of-range parameter counts, command races if semaphore handling regresses, firmware not loaded, frequency-table discovery causing visible temporary p-state changes, and resume PMAP mismatch. Test signals include firmware magic validation, successful P-state enumeration, interrupt and polling command completion, cpufreq transitions, suspend/resume restore, and meaningful `brcm_avs_*` sysfs attribute output.
