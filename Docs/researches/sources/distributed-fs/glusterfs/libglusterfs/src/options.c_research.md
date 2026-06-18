# sources/distributed-fs/glusterfs/libglusterfs/src/options.c

## Purpose
`options.c` validates translator volume options, discovers option descriptors by key pattern, normalizes deprecated aliases to preferred keys, validates whole translator graphs before activation/reconfiguration, and provides typed option initialization/reconfiguration helpers through macros from `options.h`.

## Important APIs, Types, And Functions
Public entry points include `xlator_option_validate()`, `xlator_option_validate_addr_list()`, `xlator_volume_option_get_list()`, `xlator_volume_option_get()`, `xlator_options_validate_list()`, `xlator_options_validate()`, `xlator_validate_rec()`, `graph_reconf_validateopt()`, `xlator_tree_reconfigure()`, and `xlator_option_info_list()`. The file also defines macro-expanded `xlator_option_init_*()` and `xlator_option_reconf_*()` functions for string, integer, size, percent, bool, xlator, path, double, and time types.

Validators cover path, int, size, bool, xlator name, string enum/pattern, percent, percent-or-size, time, double, internet address, internet address list, priority list, size list, arbitrary values, and client mount auth addresses. Support helpers validate IPv4 subnet notation, mount auth wildcard/host/IP patterns, list `key:value` elements, and stripe-style size multiples.

## Control Flow
`xlator_option_validate()` dispatches by `volume_option_t.type` through a static validator table. Individual validators parse strings with common utility conversion functions and enforce min/max according to `opt->validate` and `opt->min/max`. String validators match configured allowed values with `fnmatch()`. Address-list validation supports both old comma-separated address lists and newer `/dir(addr|addr),...` entries.

Whole-option validation iterates a dict with `dict_foreach()`. `xl_opt_validate()` finds the matching option descriptor, validates the data string, records an error string on failure, and if the matched key is a deprecated alias, inserts the preferred key into the dict and deletes the old key. `xlator_validate_rec()` recursively validates children first, dynamically loads translator symbols, temporarily sets `THIS`, initializes memory accounting if needed, validates options, and restores `THIS`. Reconfiguration walks old and new trees in parallel, calls default option handling, then invokes each old translator's `reconfigure()` hook under the xlator init lock.

## State And Persistence
The module mutates the options dict when replacing aliases with preferred keys. It can initialize translator memory accounting during validation and can change runtime translator configuration during reconfigure callbacks. It does not persist options itself; glusterd/volfile management owns persistence.

## Dependencies And Integration Points
Dependencies include `fnmatch`, `glusterfs/defaults.h`, `libglusterfs-messages.h`, `dict_t`, `volume_option_t`, translator graph/list types, `xlator_dynload()`, `handle_default_options()`, `xlator_init_lock()`, address parsers, and string conversion helpers from common utils. GD2 compatibility is relevant because `volume_option_t` is shared externally.

## Risks
`xlator_option_validate()` checks `opt->type > GF_OPTION_TYPE_MAX` but then indexes validators; `GF_OPTION_TYPE_MAX` itself maps to NULL and would crash if used as a real type. `xlator_options_validate()` iterates all option lists but does not stop on first failure, so later lists may overwrite `op_errstr`. `xl_opt_validate()` comments on a possible leak when replacing `stub->errstr`. Some validators assign `*op_errstr` without checking if the pointer is non-NULL. Mutating a dict during `dict_foreach()` depends on dict iterator safety. Address validators may accept broad wildcard patterns by design, so caller security expectations must match that policy.

## Test Signals
Tests should cover every option type, min-only/max-only/both range modes, malformed numeric and fractional size inputs, alias replacement in dicts, NULL `op_errstr` handling, `GF_OPTION_TYPE_MAX` rejection, old and new address-list formats, mount auth wildcards/subnets/FQDN/IPv6, recursive graph validation ordering, dynload failure behavior, and reconfigure traversal with mismatched child lists.
