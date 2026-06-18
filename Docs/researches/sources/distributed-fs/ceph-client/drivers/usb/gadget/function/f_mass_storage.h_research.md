# sources/distributed-fs/ceph-client/drivers/usb/gadget/function/f_mass_storage.h

## Purpose

`f_mass_storage.h` declares the shared Mass Storage Function configuration contract used by `f_mass_storage.c` and legacy gadget users. It exposes module-parameter helpers, configfs option structures, LUN configuration structures, and the exported `fsg_common` management API.

## Important APIs, Types, and Functions

`struct fsg_module_parameters` holds module-style arrays for backing files, read-only flags, removable flags, CD-ROM flags, no-FUA flags, LUN count, and stall behavior. `FSG_MODULE_PARAMETERS()` and the internal parameter macros define the matching module parameters, adding `num_buffers` when `CONFIG_USB_GADGET_DEBUG_FILES` is enabled.

`struct fsg_lun_opts` and `struct fsg_opts` are configfs-facing state containers. `struct fsg_lun_config` is the per-LUN construction input, including filename, `ro`, `removable`, `cdrom`, `nofua`, and inquiry string. `struct fsg_config` is the whole-function legacy configuration, including LUN array, optional callbacks/private data, vendor/product names, stall behavior, and buffer count. Prototypes expose the common setup, LUN lifecycle, buffer lifecycle, composite-device binding, inquiry-string setup, and module-parameter conversion functions implemented in `f_mass_storage.c`.

## Control Flow

The header has no executable control flow beyond the inline `fsg_opts_from_func_inst()`. Its structures determine how allocation flows in the C file: configfs creates `fsg_opts`, each LUN directory maps to `fsg_lun_opts`, and legacy users fill `fsg_config` either directly or through `fsg_config_from_params()`.

## State and Persistence Behavior

The header defines runtime-only state layouts. `fsg_opts.refcnt` and `lock` protect configfs mutation while functions are active; `no_configfs` distinguishes legacy gadget users from configfs-created functions. Persistence is external to the header: backing file contents persist, but option structures and module parameters are in-memory kernel state.

## Dependencies and Integration Points

It depends on `<linux/usb/composite.h>` and `storage_common.h` for composite-function and LUN definitions. The exported declarations are the integration boundary for older composite gadgets and for `f_mass_storage.c` itself. Changes here affect configfs function instantiation, legacy mass-storage gadgets, and any module that consumes the exported GPL symbols.

## Risks and Test Signals

Risks are mostly contract drift: changing structure fields, flag types, or module-parameter macro behavior can break legacy callers or configfs attribute semantics. `fsg_config_from_params()` depends on `file_count` and `luns` interpretation described by this header. Test signals include compiling both configfs and legacy gadget users, module-parameter parsing for multiple LUNs, debug and non-debug builds, and ABI-like behavior of default removable LUN creation.
