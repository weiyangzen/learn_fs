<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/resource.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/resource.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/resource.h` is a thin cross-cell include wrapper for the resource manager DLI bridge. It selects the public declaration header or the private inline implementation depending on the component-specific `__INLINE_*__` macro, while always importing `system_local.h` and the component local header first.

## Important APIs, Types, and Functions

The file does not define functions directly. Its important interface is the storage-class macro pair, for example `STORAGE_CLASS_*_H` and `STORAGE_CLASS_*_C`, followed by inclusion of the matching `*_public.h` or `*_private.h`. This pattern lets host, SP, ISP, and simulation builds expose the same names as either external functions or static inline code.

## Control Flow

There is no runtime control flow in this header. Compile-time control flow is the key behavior: normal builds include the public declarations, while inline builds include the private implementation after redefining storage-class macros.

## State and Persistence Behavior

No state is owned here. Any state is in the selected local/private/public component files or in hardware registers addressed through those APIs.

## Dependencies and Integration Points

It depends on `system_local.h` for platform addresses/IDs and a component `*_local.h` for device-specific constants. It integrates with the broader AtomISP CSS include hierarchy by normalizing public/private inclusion across cells.

## Risks and Edge Cases

The main risk is include-path or macro skew: a wrong `__INLINE_*__` setting can change linkage semantics, produce duplicate definitions, or hide prototypes. Because the wrapper is shared across cell builds, local header drift can break host and firmware compilation differently.

## Test Signals

Useful signals are compile-only coverage in host and inline configurations, preprocessing checks that the expected public/private header is selected, and link tests that no duplicate or missing component symbols appear.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/resource.h -->
