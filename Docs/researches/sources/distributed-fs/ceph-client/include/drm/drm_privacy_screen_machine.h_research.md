# sources/distributed-fs/ceph-client/include/drm/drm_privacy_screen_machine.h

## Purpose
`drm_privacy_screen_machine.h` declares static machine lookup support that maps consumer device/connector pairs to privacy-screen providers when firmware topology is not discoverable generically.

## Important APIs, types, and functions
`struct drm_privacy_screen_lookup` records a list link, optional consumer `dev_id`, optional connector `con_id`, and provider `dev_name()`. APIs are `drm_privacy_screen_lookup_add`, `drm_privacy_screen_lookup_remove`, and x86/config-gated `drm_privacy_screen_lookup_init` / `drm_privacy_screen_lookup_exit`.

## Control flow
Platform code or module init installs lookup entries. Consumer lookup can then match by device name and connector name, with NULL fields acting as wildcards, and resolve the named provider. Lookup entries are removed during platform or module teardown.

## State and persistence
State is an in-memory static lookup list. It persists only for the loaded kernel/module lifetime and is empty/no-op when privacy screen support or x86 machine lookup is unavailable.

## Dependencies and integration points
The header depends on list handling and integrates with privacy-screen consumer/provider resolution, especially on x86 laptops requiring DMI or machine-specific mapping.

## Risks and test signals
Risks include too-broad wildcard matches, stale provider device names, missing removal of static entries, x86-only assumptions, and matching connector names that change across drivers. Test signals include lookup add/remove, wildcard and exact matching, config-disabled stubs, machine-specific DMI initialization, and consumer resolution on systems with multiple panels.
