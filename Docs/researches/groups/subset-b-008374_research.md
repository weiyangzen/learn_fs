# subset-b-008374 research

Grouped research for the SELinux `sepolicy` Python package files in `sources/security-integrity/selinux/python/sepolicy/sepolicy`. Each section preserves the source path for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/python/sepolicy/sepolicy/__init__.py -->
# Research: sources/security-integrity/selinux/python/sepolicy/sepolicy/__init__.py

## Purpose
This module is the main public query facade for the Python `sepolicy` package. It loads an installed or named SELinux binary policy via SETools, exposes normalized policy objects and rule searches, reads libselinux file-context and user mapping files, and provides higher-level helpers used by the CLI, generator, GUI, interface, boolean, communicate, network, and manpage layers.

## Important APIs and data
The module exports numeric info selectors (`TYPE`, `ROLE`, `ATTRIBUTE`, `PORT`, `USER`, `BOOLEAN`, `TCLASS`), rule selector strings (`ALLOW`, `AUDITALLOW`, `NEVERALLOW`, `DONTAUDIT`, `TRANSITION`, `ROLE_ALLOW`), query keys (`SOURCE`, `TARGET`, `PERMS`, `CLASS`), file-type display maps, default path-to-type mappings, and many cached query helpers.

Policy loading is centered on `_pol`. `get_installed_policy()` and `get_store_policy()` locate the highest-versioned `policy.N` file using `policy_sortkey()`. `policy(policy_file)` creates a `setools.policyrep.SELinuxPolicy` object and clears a subset of caches. `load_store_policy()`, `init_policy()`, and most query functions lazily initialize `_pol`.

`info(setype, name=None)` wraps SETools queries and returns generators of dictionaries for types, roles, attributes, ports, users, booleans, and object classes. `search(types, seinfo=None)` wraps `TERuleQuery` and `RBACRuleQuery`, normalizes rule objects through `_setools_rule_to_dict()`, and returns lists of dictionaries. Higher-level helpers derive conditionals, entrypoints, writable files, transitions, role allows, domains, roles, users, booleans, ports, file types, and boolean descriptions.

## Control flow
The common flow is lazy policy initialization, SETools query construction, conversion to plain dictionaries/strings, and optional cache storage. Rule queries are split by rule family: allow-like TE rules, transition-like TE rules, and role allow RBAC rules. File-context helpers read `file_contexts`, `.homedirs`, `.local`, `.subs`, and `.subs_dist`, normalize file class codes through `trans_file_type_str`, and build maps keyed by SELinux type or equivalence path.

Domain-oriented helpers compose lower-level data. For example, `get_writable_files(setype)` searches allow rules for `open` and `write`, expands attribute targets, filters to file types, and joins with file-context regex data. `get_bools(setype)` filters cached boolean rules for source domain and splits booleans into domain-specific and generic lists based on `gen_short_name()`. `get_entrypoints()`, `get_init_entrypoint*()`, and transition helpers bridge process transition rules to file-context path data.

## State and persistence
This module keeps extensive module-level caches: policy object, file equivalence maps, local file-context records, file-context dictionary, interface methods, type/domain/user/role/port/boolean/rule lists, and parsed boolean XML descriptions. These caches persist for the interpreter lifetime until `policy()` or `reinit()` clears them. Persistent external state is read from the host SELinux installation: binary policy files, file-context files, users configuration, active boolean states, file labels via `getfilecon`, and optional policy XML. The module itself does not write policy state.

## Dependencies and integration points
Runtime dependencies are `selinux`, SETools query classes, `sepolgen.defaults`, `sepolgen.interfaces`, `glob`, `gzip`, filesystem access, and optional `distro` for OS naming. Integration points include `generate.py` for policy module generation, `gui.py` for GTK display and DBus-driven changes, `interface.py` for interface metadata, and small CLI helpers such as `booleans.py` and `communicate.py`.

## Risks and edge cases
The global cache model is not thread-safe and can serve stale data after external semanage changes unless callers remember to call `reinit()`. `reinit()` sets `methods = None`, while `get_methods()` calls `len(methods)`, so calling `get_methods()` after `reinit()` can raise `TypeError`. `policy()` clears only some caches, leaving values such as `all_types_info`, file-context caches, login mappings, boolean XML dictionaries, and full rule caches potentially tied to a previous policy. Several helpers catch broad exceptions, hiding parsing or policy errors. `get_fcdict()` assumes base and homedir file-context files exist and raises if they do not. `gen_interfaces()` requires root when interface data is stale and exits indirectly through raised `ValueError`. XML parsing in `gen_bool_dict()` assumes description nodes exist. Rule dictionaries are loosely typed and callers must handle missing keys such as `permlist`, `transtype`, `booleans`, and `filename`.

## Test signals
Useful tests should cover policy path sorting, alias resolution in `get_real_type_name()`, `info()` result shapes for MLS and non-MLS policies, rule conversion for conditional and non-conditional rules, attribute expansion, file-context parsing including missing `.local` and `.subs` files, cache invalidation after `policy()` and `reinit()`, boolean description fallback, and behavior when SETools/libselinux calls raise. Integration tests should run against a small fixture policy or mocked SETools objects rather than a host policy only.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/python/sepolicy/sepolicy/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/python/sepolicy/sepolicy/booleans.py -->
# Research: sources/security-integrity/selinux/python/sepolicy/sepolicy/booleans.py

## Purpose
This small helper supports boolean-related policy exploration by finding target types a source domain may access for a given object class and permission list. It is essentially a thin wrapper around the main `sepolicy` query facade.

## Important APIs and control flow
`expand_attribute(attribute)` calls `sepolicy.info(sepolicy.ATTRIBUTE, attribute)` and returns the first record's `types`; if the lookup raises `RuntimeError`, it treats the input as a concrete type and returns a single-item list. `get_types(src, tclass, perm)` searches allow rules with source, class, and requested permissions, raises `TypeError` if there are no matching allow rules, filters the returned rules to entries whose `permlist` contains all requested permissions, expands each target if it is an attribute, and returns a flat list of target types.

## State and persistence
The file owns no state. It relies entirely on `sepolicy` module-level policy loading and caches. It does not persist data or modify SELinux state.

## Dependencies and integration points
The only dependency is `sepolicy`. The expected integration is from command-line tooling or higher-level analysis that wants to list type targets gated by a boolean or permission relationship.

## Risks and edge cases
The exception handling in `expand_attribute()` differs from the newer generator-return style used in `sepolicy.info()`; if an attribute is absent and the generator raises `StopIteration` instead of `RuntimeError`, the exception can escape. `get_types()` uses permissive list concatenation and does not deduplicate expanded attributes. It assumes every returned rule has a `permlist` key, which may not hold for all rule dictionaries. The error type differs from `communicate.py`, which raises `ValueError` for the same no-allow condition.

## Test signals
Tests should mock `sepolicy.search()` and `sepolicy.info()` for concrete targets, attribute targets, missing attributes, no allow rules, partial permission matches, and duplicate attribute expansion. A compatibility test should capture whether missing attribute lookup raises `RuntimeError` or `StopIteration` under the current `sepolicy.info()` implementation.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/python/sepolicy/sepolicy/booleans.py -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/python/sepolicy/sepolicy/communicate.py -->
# Research: sources/security-integrity/selinux/python/sepolicy/sepolicy/communicate.py

## Purpose
This helper provides shared CLI-style behavior for communication/access analysis. It formats usage failures and computes allowed target types for a source domain, class, and permissions.

## Important APIs and control flow
`usage(parser, msg)` prints parser help, writes an error message to stderr, flushes, and exits with status 1. `expand_attribute(attribute)` calls `next(sepolicy.info(sepolicy.ATTRIBUTE, attribute))`, converts the returned `types` iterable to a list, and falls back to `[attribute]` on `StopIteration`. `get_types(src, tclass, perm)` searches allow rules, raises `ValueError` when none exist, filters rules whose `permlist` includes the requested permission set, expands target attributes, and returns the flat target list.

## State and persistence
There is no local mutable state and no direct persistence. The module may trigger lazy loading and caching inside `sepolicy`.

## Dependencies and integration points
Dependencies are `sys` and `sepolicy`. The module is intended for CLI entry points that have an argparse-like parser and need to compute communication targets from SELinux allow rules.

## Risks and edge cases
`usage()` calls `sys.exit()`, so it is hostile to library callers unless isolated. `get_types()` assumes `perm` is iterable and suitable for `set(perm)`. Passing a string permission accidentally creates a set of characters, not a one-permission set. Like `booleans.py`, the returned target list is not deduplicated and rule dictionaries without `permlist` will raise. Its no-allow exception type differs from `booleans.py`.

## Test signals
Tests should cover `usage()` output and exit, missing attributes, concrete targets, attribute expansion, no allow rules, string-versus-list permissions, and duplicate outputs. CLI tests should assert stderr flushing and exit code behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/python/sepolicy/sepolicy/communicate.py -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/python/sepolicy/sepolicy/generate.py -->
# Research: sources/security-integrity/selinux/python/sepolicy/sepolicy/generate.py

## Purpose
`generate.py` implements `policygentool`-style SELinux policy module generation. It collects requested application/user policy options, discovers host policy, ports, RPM ownership, writable paths, init scripts, and ELF symbol hints, then renders `.te`, `.if`, `.fc`, `.spec`, and setup shell script output from template modules under `sepolicy.templates`.

## Important APIs and types
Top-level helpers include `get_rpm_nvr_from_header()`, `get_rpm_nvr_list()`, `get_all_ports()`, `get_all_users()`, `get_poltype_desc()`, and `verify_ports()`. Constants define generated policy categories: daemons, DBus daemons, inetd services, CGI scripts, sandbox modules, application domains, existing domains, login user roles, root/admin roles, and new types.

The central type is class `policy`. Its constructor validates the module name/type, initializes host policy data (`get_all_roles()`, `get_all_ports()`), defines symbol-to-action heuristics, default path buckets and template modules, type-specific generator dispatch, and mutable generation state such as capabilities, process permissions, network flags, booleans, custom files/dirs, admin/transition domains, users, roles, and program/init script paths.

Public setters include `set_program()`, `set_init_script()`, `set_in_tcp()`, `set_in_udp()`, `set_out_tcp()`, `set_out_udp()`, feature toggles for resolver/syslog/Kerberos/PAM/DBus/audit/etc/localization/fd/terminal/mail/tmp/UID, and collection mutators for capabilities, processes, booleans, files, dirs, admin domains, existing domains, transition domains/users, roles, and new types.

## Control flow
Generation is staged. Inputs populate instance state; `gen_writeable()` and `gen_symbols()` can infer additional state from the host package database, filesystem, init script locations, and `nm -D` output. Type-specific methods render base type declarations and rules. Cross-cutting methods render capabilities, process permissions, network types/rules, file-context records, booleans, user/role transitions, admin rules, DBus/sandbox/admin interfaces, package specs, and setup scripts.

`generate_te()` is the main type-enforcement assembler: it emits default type declarations, selected default-directory types, a local policy marker for most module types, optional capability/process/network/tmp/boolean/default rules, per-directory template rules, and feature-specific rules. `generate_if()`, `generate_fc()`, `generate_sh()`, and `generate_spec()` assemble the other artifacts. `generate(out_dir)` writes files by calling `write_te()`, `write_if()`, `write_fc()`, and, except for `NEWTYPE`, `write_spec()` and `write_sh()`.

## State and persistence
Instance state is long-lived and accumulates user options and discovered resources. Output persistence is direct file creation in `out_dir`; generated setup scripts are chmodded `0750`. Host-state reads include SELinux policy data, active ports, RPM database, DNF/libdnf package metadata, filesystem paths under `/var`, `/etc/rc.d/init.d`, and dynamic symbols from the executable. The module does not apply policy itself; it emits artifacts and scripts.

## Dependencies and integration points
Dependencies include `sepolicy`, selected `sepolicy` query functions, libselinux indirectly, `sepolgen.interfaces/defaults`, many `sepolicy.templates` modules, optional `rpm`, optional `libdnf5` or `dnf`, `nm`, `grep`, and filesystem metadata via `os`/`stat`. It integrates with CLI front ends that gather user choices and with RPM packaging workflows through generated spec/setup scripts.

## Risks and edge cases
The code has Python 3 compatibility hazards: `get_poltype_desc()` calls `keys.sort()` on a `dict_keys` view. `verify_ports()` accepts port `65536` even though TCP/UDP ports stop at `65535`. `get_all_users()` blindly removes `system_u` and `root`, which can raise if a policy lacks either. `set_use_tmp()` updates default path buckets but never assigns `self.use_tmp`, so tmp rules/types may not be generated consistently. Symbol heuristics have duplicate keys, so earlier mappings are overwritten; for example multiple `openlog` and `pam_` assignments collapse to the last value. `gen_symbols()` uses `os.popen("nm -D %s | grep U" % self.program)` without shell quoting and then `exec()` on hardcoded action strings, making executable paths with shell metacharacters dangerous. Path bucketing in `__find_path()` depends on dictionary iteration order and may match broader prefixes before narrower paths. The DNF/RPM discovery code reads available packages, not necessarily installed packages, and may add paths based on package metadata that do not exist locally. Many file writes use plain `open()` without atomic replacement or error cleanup.

## Test signals
Tests should exercise every policy type's generated `.te/.if/.fc/.spec/.sh` shape with deterministic templates, port parsing including invalid ranges and boundaries, network rule generation for known and unknown port types, default path bucketing, `NEWTYPE` suffix validation, required existing-domain/program errors, RPM/DNF discovery with mocked package APIs, shell-symbol scanning without invoking a real shell, and output file permissions. Regression tests should cover `set_use_tmp()`, `get_poltype_desc()`, and unsafe program paths.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/python/sepolicy/sepolicy/generate.py -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/python/sepolicy/sepolicy/gui.py -->
# Research: sources/security-integrity/selinux/python/sepolicy/sepolicy/gui.py

## Purpose
`gui.py` implements the GTK 3 graphical SELinux policy management application. It displays domains, booleans, file labels, network ports, transitions, login mappings, SELinux users, file equivalences, lockdown toggles, current/default enforcement mode, policy type, relabel state, and import/export functions. It stages user edits in memory and applies them through an SELinux DBus service.

## Important APIs and structure
The module defines page constants, display strings, a `cmp()` helper, reverse file-type mapping, and class `SELinuxGui`. Construction loads `/usr/lib*/python*/site-packages/sepolicy/sepolicy.glade` via `Gtk.Builder`, creates `SELinuxDBus`, obtains existing customized policy state, wires hundreds of widgets, builds the domain/application completion list from `sepolicy.get_all_domains()` and init entrypoints, connects signal handlers, initializes status polling with `GLib.timeout_add_seconds()`, and enters `Gtk.main()`.

Core state includes `cur_dict` for staged changes by semanage category, `cust_dict` for existing customized records parsed from `dbus.customized()`, selected `application`, page pointers (`opage`, tree/list/filter references), DBus handle, local file-context data, status/enforcement widgets, and popup/update window state.

## Control flow
Application selection clears current liststores, resolves executable paths to domains when needed, refreshes DBus customized state, calls `sepolicy.reinit()`, repopulates booleans, executable files, network ports, writable files, transitions, app file types, and file transitions, then updates labels/tooltips.

Display initialization methods read from `sepolicy` and `sepolicy.network`: `boolean_initialize()`, `executable_files_initialize()`, `writable_files_initialize()`, `application_files_initialize()`, `network_initialize()`, `transitions_*_initialize()`, `user_initialize()`, `login_initialize()`, and `file_equiv_initialize()`. Filtering is implemented through GTK tree model visible functions. Add/modify/delete handlers open popups, collect values, validate simple file/port inputs, update liststores, and stage semanage-like operations in `cur_dict`.

Applying changes is a two-step flow: `update_or_revert_changes()` renders a confirmation tree in `update_gui()`, then `apply_changes_button_press()` either calls `update_the_system()` or removes unchecked changes through `revert_data()`. `update_the_system()` builds a newline-separated semanage command buffer with `format_update()` and sends it to `self.dbus.semanage()`. System-level actions call DBus immediately: setenforce, default mode, default policy type, relabel-on-boot, restorecon, module enable/disable, deny_ptrace, import config, and export config.

## State and persistence
GUI state is mostly in GTK liststores plus `cur_dict` and `cust_dict`. Persistent system effects are delegated to `SELinuxDBus`: semanage operations, enforcement changes, default mode/policy changes, relabel marker changes, module toggles, and restorecon. Export writes the customized policy buffer to a user-chosen file; import reads a file and passes its contents to DBus semanage. The GUI also reads live file labels and default contexts to mark mislabeled files.

## Dependencies and integration points
Dependencies are PyGObject GTK/GDK/GLib, DBus, `sepolicy.sedbus.SELinuxDBus`, `sepolicy`, `sepolicy.network`, `sepolicy.manpage`, `selinux`, filesystem access, regex, Unicode normalization, and Glade/help/image files installed under the `sepolicy` Python package path. It integrates the query facade in `__init__.py` with a privileged DBus backend that applies policy changes.

## Risks and edge cases
Several paths appear bug-prone or broken. `update_gui()` expects boolean staged entries to contain `action`, but `on_toggle()` stores only `active`. `format_update()` tests `if k in "boolean"` and similar string-membership expressions instead of equality; this is fragile and can execute the wrong block for short key names. The fcontext and port formatting paths reference missing or wrong keys: file updates store no `class` value, port updates use `self.cur_dict[k][f]` where `f` is from another loop or undefined, and modify paths call nonexistent `self.unmark()` while also using `set_value()` where `get_value()` was intended. `update_to_file_equiv()` similarly calls `set_value()` while reading old values. User modification records `oldlevel` from column 1 instead of column 2. Network validation accepts only one integer port, while the UI and semanage allow ranges/lists elsewhere. Many broad exception handlers hide DBus, parsing, and policy errors. Import passes arbitrary file content to privileged semanage through DBus after only file selection. `fix_mislabeled()`, default policy changes, module toggles, and enforcement changes produce immediate system effects with limited rollback. The constructor starts `Gtk.main()`, making the class hard to unit-test directly despite the `test` flag.

## Test signals
Useful tests include widget-independent unit tests for `previously_modified_initialize()`, `format_update()`, `revert_data()`, `error_check_files()`, `error_check_network()`, `autofill_add_files_entry()`, `recursive_path()`, and `filter_the_data()`. DBus should be mocked for apply/import/export/system toggles. Integration tests should load the Glade file in a headless GTK environment and simulate add/modify/delete flows for booleans, fcontexts, ports, users, logins, and file equivalences. Regression tests should specifically cover boolean apply, fcontext modify, port add/modify, file-equivalence modify, and `sepolicy.reinit()` followed by application refresh.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/python/sepolicy/sepolicy/gui.py -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/python/sepolicy/sepolicy/help/__init__.py -->
# Research: sources/security-integrity/selinux/python/sepolicy/sepolicy/help/__init__.py

## Purpose
This file is an empty package marker for `sepolicy.help`. It allows the help directory to be treated as a Python package alongside text and image assets loaded by `gui.py`.

## Important APIs and control flow
There are no functions, classes, constants, imports, or executable statements. Importing the package has no side effects.

## State and persistence
There is no local state and no persistence behavior.

## Dependencies and integration points
The practical integration point is the GUI help system, which constructs paths such as `code_path + "help/<topic>.txt"` and `code_path + "help/<topic>.png"`. This `__init__.py` does not participate directly in those file reads but preserves package layout for installers and import tooling.

## Risks and edge cases
The file has no runtime risk by itself. Packaging tests should ensure it is included with the help assets if the distribution expects `sepolicy.help` to be importable.

## Test signals
A minimal test can import `sepolicy.help` and verify no side effects. Packaging checks should confirm adjacent help text/image resources are installed where `gui.py` expects them.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/python/sepolicy/sepolicy/help/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/python/sepolicy/sepolicy/interface.py -->
# Research: sources/security-integrity/selinux/python/sepolicy/sepolicy/interface.py

## Purpose
`interface.py` exposes SELinux policy interface metadata. It reads generated policy XML or converts `.if` interface files to XML, lists interfaces, identifies admin and user-role interfaces, formats interface summaries, generates compile-test TE modules, and optionally invokes the SELinux development Makefile to validate interface compilation.

## Important APIs and control flow
The public surface is declared in `__all__`: `get_all_interfaces()`, `get_interfaces_from_xml()`, `get_admin()`, `get_user()`, `get_interface_dict()`, `get_interface_format_text()`, `get_interface_compile_format_text()`, `get_xml_file()`, and `interface_compile_test()`.

`get_all_interfaces(path="")` either delegates to `sepolicy.get_methods()` for installed policy or converts/parses a supplied interface file. `get_interface_dict(path)` parses XML layers/modules/interfaces/templates with `xml.etree.ElementTree`, storing each interface name as `[param_names, summary_text, "interface"|"template"]` in a module-global cache. `get_admin()` and `get_user()` filter interface names ending in `_admin` or `_role`; installed-policy mode returns stripped domain prefixes, while path mode returns full matching interface names and checks role interfaces against `sepolicy.get_all_types()`. Formatting helpers render human-readable signatures or compile-call stubs using `.templates.test_module.dict_values`. `get_xml_file(if_file)` shells out to `/usr/share/selinux/devel/include/support/segenxml.py`. `interface_compile_test()` writes temporary compile-test files, runs `make -f /usr/share/selinux/devel/Makefile compiletest.pp`, reports failures, and deletes generated files.

## State and persistence
The only module state is `interface_dict`, a global cache that persists after the first parse. `interface_compile_test()` writes and deletes `compiletest.te`, `compiletest.fc`, `compiletest.if`, and `compiletest.pp` in the current working directory; failed or interrupted runs could leave files behind. `get_xml_file()` and compile tests depend on installed SELinux development files.

## Dependencies and integration points
Dependencies include `re`, `sys`, `sepolicy`, gettext, XML parsing, `subprocess.getstatusoutput` or legacy `commands`, `os`, templates from `.templates.test_module`, the `segenxml.py` converter, and the SELinux devel Makefile. It integrates with the main `sepolicy` interface method cache and with policy development tooling that validates interface calls.

## Risks and edge cases
`get_interface_dict()` caches without considering the path argument, so the first parsed policy XML is returned for all later paths. XML parsing assumes `summary` nodes exist and have text. `get_xml_file()` builds a shell command with an unquoted path, so interface file paths containing shell metacharacters can change command behavior. `interface_compile_test()` writes fixed filenames in the current directory, so concurrent runs collide and user files with the same names can be overwritten/deleted. It shells out through `getstatusoutput()` and depends on system Python/devel paths. Several error paths call `sys.exit(1)`, which is inconvenient for library callers. Installed-policy and path modes return different name shapes for admin/user helpers.

## Test signals
Tests should parse fixture XML containing interfaces, templates, parameters, and summaries; validate `get_admin()`/`get_user()` in both path and installed-policy modes; check cache behavior when different paths are requested; verify formatting against `test_module.dict_values`; mock `getstatusoutput()` for XML conversion and compile success/failure; and run compile-test logic in a temporary directory to ensure cleanup and no accidental overwrite.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/python/sepolicy/sepolicy/interface.py -->
