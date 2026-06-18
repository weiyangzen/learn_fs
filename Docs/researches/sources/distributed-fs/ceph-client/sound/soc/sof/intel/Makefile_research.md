# sources/distributed-fs/ceph-client/sound/soc/sof/intel/Makefile

Purpose: this Makefile maps the Kconfig symbols in the same directory to loadable or built-in SOF Intel objects. It defines composite modules for ACPI Atom/Broadwell support, the shared HDA common layer, HDA generic glue, HDA link codecs, HDA multi-link, SoundWire bridge pieces, and PCI family drivers.

Important build products: `snd-sof-acpi-intel-byt-y` and `snd-sof-acpi-intel-bdw-y` are narrow ACPI modules. `snd-sof-intel-hda-common-y` is the large common module containing loader, stream, trace, DSP, IPC, controller, PCM, DAI, bus, telemetry, and tracepoint code, with optional `hda-probes.o`. `snd-sof-intel-hda-generic-y` adds `hda.o` and common ops. Per-family PCI modules pair discovery glue such as `pci-apl.o` or `pci-cnl.o` with generation-specific operation files such as `apl.o`, `cnl.o`, or `hda-loader-skl.o`.

Control flow and integration: the object graph mirrors the runtime architecture. Kconfig chooses a platform symbol, the Makefile emits the corresponding object, and the platform object installs `snd_sof_dsp_ops` and `sof_intel_dsp_desc` structures used by the SOF core. `CONFIG_SND_SOC_SOF_HDA_COMMON`, `CONFIG_SND_SOC_SOF_HDA_GENERIC`, and `CONFIG_SND_SOC_SOF_HDA` intentionally separate core HDA DSP support from generic PCI matching and legacy HDA codec support.

State and persistence behavior: no runtime state is stored here, but build outputs persist as module boundaries and namespace exports. Moving a source file between composite targets changes symbol visibility and module load ordering, especially for namespace-imported symbols.

Dependencies and risks: the risk is mismatching Kconfig and object membership. For example, enabling CNL-family ops requires the common HDA object that exports `hda_dsp_*`, `hda_ipc*`, and DAI helpers. Optional probes and SoundWire bridge objects must stay behind their config gates. Test signals are kernel module link success, `modpost` namespace warnings, and boot/probe logs confirming the selected platform module loads with the expected common module.
