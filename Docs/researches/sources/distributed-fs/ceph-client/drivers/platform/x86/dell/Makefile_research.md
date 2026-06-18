# sources/distributed-fs/ceph-client/drivers/platform/x86/dell/Makefile

Purpose: Maps Dell Kconfig symbols to object files and composite module members.

Important build rules: `alienware-wmi.o` is composed from base plus optional legacy/WMAX files. `dell-smbios.o` is composed from base plus optional WMI/SMM backends. `DELL_SMO8800` builds both `dell-smo8800.o` and `dell-lis3lv02d.o`.

Control flow/state/persistence: No runtime behavior. It controls link composition and module contents.

Dependencies/integration: Coordinates with Kconfig symbols and includes the `dell-wmi-sysman/` subdirectory object when selected.

Risks/test signals: Missing conditional object entries cause unresolved symbols or missing features. Test with `make M=drivers/platform/x86/dell` across representative config combinations.
