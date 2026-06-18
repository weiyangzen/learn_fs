# sources/distributed-fs/ceph-client/sound/soc/sof/Kconfig

Purpose: top-level Kconfig menu for Sound Open Firmware support, enumeration transports, client/debug features, IPC versions, and vendor platform subtrees.

Important APIs/types/functions: defines `SND_SOC_SOF_TOPLEVEL`, transport symbols (`SND_SOC_SOF_PCI`, `SND_SOC_SOF_ACPI`, `SND_SOC_SOF_OF` plus internal `*_DEV` symbols), core `SND_SOC_SOF`, IPC symbols `SND_SOC_SOF_IPC3` and `SND_SOC_SOF_IPC4`, compress/probes/client symbols, and developer/debug options such as nocodec, strict ABI, IPC fallback, firmware trace, IPC flood/injector clients, retained DSP context, and probe workqueue.

Control flow: user-visible transport/platform selections select hidden implementation symbols. Developer options are gated behind `EXPERT && SND_SOC_SOF`, then further nested debug controls appear under `SND_SOC_SOF_DEBUG`. At the end, it sources AMD, i.MX, Intel, MediaTek, and Xtensa Kconfig files.

State and persistence: build-time configuration only. These symbols shape which objects compile and which runtime module parameters/features are available.

Dependencies and integration points: integrates with PCI, ACPI, OF, auxiliary bus, compressed audio, and vendor Kconfigs. `SND_SOC_SOF` selects topology and optional nocodec support.

Risks: many options are hidden and selected indirectly, so dependency mistakes can produce missing objects or unusable debug clients. Developer options can alter runtime behavior significantly, especially nocodec, strict ABI, fallback IPC version, and retained DSP context.

Test signals: build matrix coverage across PCI/ACPI/OF and IPC3/IPC4 is the main signal; runtime behavior is validated by platform probes and SOF firmware boot tests.
