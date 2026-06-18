# sources/distributed-fs/ceph-client/include/linux/netfilter_bridge/ebtables.h

Purpose: Declares the ebtables bridge filtering framework types for bridge matches, watchers, targets, tables, stack handling, and registration.

Important APIs, types, and functions: Important types are `struct ebt_match`, `struct ebt_watcher`, `struct ebt_target`, `struct ebt_chainstack`, `struct ebt_table_info`, and `struct ebt_table`. APIs register/unregister tables/templates and run `ebt_do_table()`. Detected source surface: 127 lines; includes `linux/if.h`, `linux/if_ether.h`, `uapi/linux/netfilter_bridge/ebtables.h`; macros `BASE_CHAIN`, `CLEAR_BASE_CHAIN_BIT`, `EBT_ALIGN`, `__LINUX_BRIDGE_EFF_H`; structs `ebt_chainstack`, `ebt_counter`, `ebt_entries`, `ebt_entry`, `ebt_match`, `ebt_replace_kernel`, `ebt_table`, `ebt_table_info`, `ebt_target`, `ebt_watcher`, `list_head`, `module`, `nf_hook_ops`; enums none; typedefs none; function-like declarations/helpers `ebt_do_table`, `ebt_invalid_target`, `ebt_register_table`, `ebt_register_template`, `ebt_unregister_table`, `ebt_unregister_table_pre_exit`, `ebt_unregister_template`, `int`.

Control flow: Bridge packets traverse ebtables chains, invoking match callbacks, watcher callbacks for side effects, and target callbacks for verdicts. Table registration installs initial entries and private table info.

State and persistence behavior: Per-net table state includes entries, counters, hook entry offsets, underflow pointers, chain stack, and initial entries. Module registration state tracks matches, watchers, and targets.

Dependencies and integration points: Depends on network interface, Ethernet, UAPI ebtables, x_tables alignment, and bridge hook definitions.

Risks and test signals: Risks are invalid target verdicts, chain stack overflow, counter races, and compat/layout mismatch with userspace ebtables. Test bridge filter/nat/broute tables, watcher side effects, base-chain underflows, and module unload.
