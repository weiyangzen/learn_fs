# sources/distributed-fs/ceph-client/drivers/misc/ocxl/pci.c

Purpose: PCI driver binding for generic OpenCAPI devices using IBM device ID `0x062B`; opens the OCXL function and registers discovered AFUs with the file layer.

Important APIs and functions: `ocxl_probe()` opens the function with `ocxl_function_open()`, stores it in PCI drvdata, gets the AFU list with `ocxl_function_afu_list()`, and calls `ocxl_file_register_afu()` for each AFU. `ocxl_remove()` unregisters each AFU and closes the function. `ocxl_pci_driver` defines probe/remove/shutdown hooks and the PCI ID table.

Control flow: probe tolerates individual AFU registration failures by logging and continuing, relying on `ocxl_file_register_afu()` cleanup. Remove iterates AFUs and unregisters file devices before closing the function. Shutdown reuses remove behavior.

State and persistence: the PCI device stores `struct ocxl_fn *` in drvdata. AFU/file/link state is allocated by lower layers and released on remove.

Dependencies and integration points: integrates generic PCI matching, OCXL function discovery/config parsing, and character/sysfs registration. It is registered by `main.c`.

Risks and test signals: partial AFU registration can leave a function open with only some AFUs exposed; tests should cover sparse AFU lists and failures in file registration. Hot-unplug/shutdown tests should ensure unregister order prevents use-after-free and no AFU device node remains after `ocxl_function_close()`.
