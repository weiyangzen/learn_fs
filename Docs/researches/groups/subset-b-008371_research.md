# subset-b-008371 research

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/python/semanage/semanage -->
# sources/security-integrity/selinux/python/semanage/semanage

## Purpose
This executable Python entrypoint implements the `semanage` command-line interface for local SELinux policy management. It is almost entirely a parser and dispatcher layer: it defines subcommands, validates required and conflicting options, translates legacy import/export syntax, then delegates actual policy-store mutation and listing to record classes in `seobject.py`.

## Important APIs, types, and functions
- `CheckRole(argparse.Action)` validates `semanage user -R` role arguments through `sepolicy.get_all_roles()`, treating an unloadable policy as an empty valid-role set.
- `seParser` customizes `argparse.ArgumentParser.error()` so single-argument invocations show full help while normal parse errors show usage.
- `SetExportFile` and `SetImportFile` redirect `stdout`/`stdin` for `export -f` and `import -f`; `-` preserves the current stream.
- `object_dict` maps subcommand names to `seobject` record classes: login, SELinux user, port, module, interface, node, fcontext, boolean, permissive, dontaudit, ibpkey, and ibendport.
- `generate_custom_usage()` builds hand-written usage strings for complex subcommands.
- `handle_opts()` enforces action-specific conflicts and required arguments after argparse has accepted the command shape.
- `handleLogin`, `handleFcontext`, `handleUser`, `handlePort`, `handlePkey`, `handleIbendport`, `handleInterface`, `handleModule`, `handleNode`, `handleBoolean`, `handlePermissive`, `handleDontaudit`, `handleExport`, and `handleImport` are the command handlers.
- `mkargv()` tokenizes semanage import lines, preserving simple single- and double-quoted arguments.
- `createCommandParser()`, `make_io_args()`, `make_args()`, and `do_parser()` compose the CLI and run it.

## Control flow
Startup calls `do_parser()`, which creates the top-level parser, converts legacy `-o`/`-i` import/export invocations when needed, parses `sys.argv`, and invokes `args.func(args)`. Each setup function installs one subparser and sets a handler default. Handlers call `handle_opts()` to enforce semantic requirements, instantiate the matching `seobject` class with the parsed namespace, and call the method matching `args.action`.

`handleExport()` emits a delete-all command for every managed item, then walks each record class's `customized()` output to produce replayable local customizations. `handleImport()` starts a `seobject.semanageRecords` transaction, separates destructive lines containing `-d` or `-D` from the rest, applies destructive commands first through `importHelper()`, finishes, starts a second transaction, and applies all remaining commands. `importHelper()` reparses each imported command through a fresh command parser, so import shares the normal handler paths.

## State and persistence behavior
The file itself persists no SELinux policy data. It mutates process-level I/O by assigning `sys.stdout` and `sys.stdin` for import/export files. Persistent effects occur through `seobject` methods, which write libsemanage local customizations and commit transactions unless `--noreload` is set. Import mode relies on the class-level transaction state in `seobject.semanageRecords` to group multiple parsed commands.

## Dependencies and integration points
The script depends on Python `argparse`, `gettext`, `os`, `re`, `sys`, and `traceback`, plus local `seobject` and policy introspection from `sepolicy` for role validation. It is tightly coupled to method signatures in `seobject.py`; the parser's destination names (`login`, `seuser`, `range`, `type`, `proto`, `subnet_prefix`, `ibdev_name`, and so on) are passed directly to those methods. It also integrates with SELinux translations by using gettext domain `selinux-python`.

## Risks and edge cases
- Several `handle_opts()` dictionaries contain misspelled option names such as `localist`, `prototype`, and `subnet prefix`. Those entries do not match argparse destinations, so intended conflict checks are skipped for some actions.
- `handle_opts()` treats each dictionary entry as `(conflicts, required)`, but the `handleIbendport` `add` entry has a third tuple element that is ignored. This is harmless at runtime but signals uneven table maintenance.
- Import delete-command detection uses substring checks for `"-d"` and `"-D"` across the full line, so a value containing those strings can be classified as a deletion command.
- `mkargv()` is a small custom tokenizer, not shell-compatible quoting. It can mishandle escapes, malformed quotes, and complex import files.
- `SetExportFile` catches all exceptions and prints a traceback, exposing internal details but avoiding silent failure.
- The CLI layer is the only enforcement for many required parameters. Misspelled `handle_opts()` keys can let bad inputs reach libsemanage wrappers, where errors may be less user-friendly.

## Test signals
`test-semanage.py` exercises list, extract, import/export compatibility, fcontext, port, login, user, and boolean flows. It does not cover ibpkey, ibendport, module enable/disable/remove, dontaudit toggling, malformed import quoting, or the typoed option-conflict paths. Runtime testing requires SELinux enforcing mode and host tools such as `semanage`, `useradd`, and `userdel`.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/python/semanage/semanage -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/python/semanage/semanage-bash-completion.sh -->
# sources/security-integrity/selinux/python/semanage/semanage-bash-completion.sh

## Purpose
This Bash completion script provides tab completion for the `semanage` CLI. It offers subcommand names, common options, and policy-derived completions for stores, SELinux users, roles, types, modules, domains, file types, and protocol values.

## Important APIs, types, and functions
- `__contains_word()` tests whether a word is present in a list.
- `ALL_OPTS` and `MANAGED_OPTS` define shared option groups.
- `__get_all_stores()`, `__get_all_users()`, `__get_all_types()`, `__get_all_port_types()`, `__get_all_domains()`, `__get_all_node_types()`, `__get_all_file_types()`, `__get_all_roles()`, and `__get_all_modules()` query host policy state through `/etc/selinux`, `seinfo`, and `semodule`.
- `__get_*_opts()` functions return option sets by subcommand.
- `_semanage()` is the actual completion function registered by `complete -F _semanage semanage`.

## Control flow
When Bash asks for completions, `_semanage()` inspects `COMP_WORDS[1]`, the current word, and the previous word. It first handles value completions for permissive domains and module enable/disable/remove/remove arguments. It then decides whether the user is completing the subcommand, a value for a recognized option (`-S`, `-p`, `-R`, `-s`, `-f`, or `-t`), or options for the current subcommand. Results are generated with `compgen -W`.

## State and persistence behavior
The script has no persistence. It reads system policy state and command outputs at completion time. `COMPREPLY` is the only mutated shell state.

## Dependencies and integration points
It depends on Bash completion variables, `compgen`, `/etc/selinux`, `dir`, `grep`, `cut`, `seinfo`, and `semodule`. The completion vocabulary must stay aligned with the Python `semanage` parser. It currently lists the main verbs `boolean`, `dontaudit`, `export`, `fcontext`, `import`, `interface`, `login`, `module`, `node`, `permissive`, `port`, and `user`; it does not include the Python CLI's Infiniband `ibpkey` and `ibendport` subcommands.

## Risks and edge cases
- `__get_all_stores()` is defined twice.
- The function declares `local verb comps` but never assigns `verb`; branches effectively rely on `$command` and empty `$verb`.
- The `-t` completion branch checks `--types`, while the CLI uses `--type`, so long-option type completion may not trigger.
- `__get_import_opts()` and `__get_export_opts()` advertise `--f`, but the CLI uses `-f` plus `--input_file` or `--output_file`.
- `__get_boolean_opts()` includes `-off` rather than `--off`.
- Completion for protocols only suggests `tcp udp`, omitting `dccp` and `sctp` supported by `semanage port`; node `ipv4`/`ipv6` completion is not separated from port protocol completion.
- Policy queries can be slow or absent on minimal systems; stderr is suppressed for `seinfo` but not all helpers.

## Test signals
There is no dedicated completion test. Useful smoke tests would source the script in Bash, set `COMP_WORDS` and `COMP_CWORD` for representative command lines, and verify options and value completions match the Python parser.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/python/semanage/semanage-bash-completion.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/python/semanage/seobject.py -->
# sources/security-integrity/selinux/python/semanage/seobject.py

## Purpose
`seobject.py` is the backend implementation for the `semanage` CLI. It wraps libsemanage Python bindings and SELinux/sepolicy/setools helpers to manage local policy customizations for modules, permissive domains, logins, SELinux users, ports, Infiniband pkeys/end ports, nodes, interfaces, file contexts, and booleans.

## Important APIs, types, and functions
- Global maps `file_types`, `file_type_str_to_option`, and `ftype_to_audit` translate CLI file-type names to libsemanage constants, CLI options, and audit-resource labels.
- `logger` has two implementations: an audit-backed implementation using `audit.audit_log_semanage_message()`/`audit.audit_log_user_comm_message()`, and a syslog fallback. `nulllogger` suppresses logging for alternate stores.
- `validate_level()`, `translate()`, and `untranslate()` validate and convert MLS/MCS labels through `selinux_*_context` APIs.
- `semanageRecords` owns the shared libsemanage handle, selected store, transaction flag, begin/commit/finish lifecycle, `--noreload`, and common error handling.
- Record classes implement object-specific operations:
  - `moduleRecords`: list/install/remove/enable/disable modules and reset disabled modules.
  - `dontauditClass`: toggles disable-dontaudit state.
  - `permissiveRecords`: creates/removes `permissive_<type>` CIL modules.
  - `loginRecords`: manages Linux login or `%group` mappings to SELinux users and ranges.
  - `seluserRecords`: manages SELinux users, roles, prefix, MLS level, and range.
  - `portRecords`: manages protocol/port or range to type/range mappings.
  - `ibpkeyRecords` and `ibendportRecords`: manage Infiniband pkey and end-port contexts.
  - `nodeRecords`: manages IPv4/IPv6 network node contexts.
  - `interfaceRecords`: manages network interface contexts.
  - `fcontextRecords`: manages file-context regexes and equivalence substitutions.
  - `booleanRecords`: manages persistent and active boolean values.

## Control flow
Each record class follows a common public pattern: `add()`, `modify()`, `delete()`, and `deleteall()` call `begin()`, run a private `__add`/`__modify`/`__delete`, then `commit()`. Add operations usually modify an existing record when one already exists. Delete operations usually refuse to remove non-local policy records. List and `customized()` methods query libsemanage lists and format either human-readable output or replayable semanage fragments.

The base constructor creates or reuses a process-global semanage handle, selects an alternate store when requested, connects to the store, records whether MLS is enabled in the global `is_mls_enabled`, and chooses an audit/syslog/no-op logger. `handleImport()` in the CLI uses `semanageRecords.start()` and `finish()` so nested record operations join one transaction instead of committing individually.

## State and persistence behavior
Persistent state is written to the SELinux policy store via libsemanage local customization APIs and `semanage_commit()`. The class-level `semanageRecords.handle`, `store`, and `transaction` make all record objects in a process share a connection and transaction state. `commit()` honors `--noreload` by calling `semanage_set_reload(self.sh, 0)` before committing. `fcontextRecords` has an additional persistence path: equivalence rules are loaded from `selinux_file_context_subs_path()` and `_dist_path()`, then local substitutions are rewritten through a temp file and `os.rename()` when `equal_ind` is set. `booleanRecords` may also set active runtime booleans with `semanage_bool_set_active()` when modifying the current store.

## Dependencies and integration points
This module imports `pwd`, `grp`, `selinux`, `os`, `re`, `sys`, `stat`, `socket`, `ipaddress`, `syslog`, `sepolicy`, `setools.policyrep.SELinuxPolicy`, `setools.typequery.TypeQuery`, and all names from the generated `semanage` libsemanage binding. The CLI depends on these classes and method signatures. SELinux policy state is also read through `selinux.getseuserbyname()`, `/logins` under the policy root, sepolicy attribute queries, setools type queries for Infiniband types, and boolean description/category helpers.

## Risks and edge cases
- The shared class-level handle and transaction flag make this module process-global and not safe for independent concurrent use in one interpreter.
- Alternate policy stores set global SELinux policy root with `selinux.selinux_set_policy_root()`, which can affect later calls in the same process.
- Many libsemanage return codes are checked, but some setter return values are ignored after query success, which can hide partial failures until commit.
- `ibpkeyRecords.__exists()` calls `.formnat(...)` on a string in one error path, producing `AttributeError` instead of the intended `ValueError` if key existence checking fails.
- `ibendportRecords.add()` formats a message with undefined `port` when an entry already exists, causing `NameError` on that path.
- In `moduleRecords.get_all()`, sorting is described as higher priorities first, but the first sort key is language extension and then name; priority ordering is not actually applied.
- `fcontextRecords.commit()` writes equivalence substitutions outside libsemanage's usual object API. It uses a temp file and rename, but does not explicitly fsync or lock the file.
- `booleanRecords.customized()` emits `-%s` using numeric active state values, producing `-0`/`-1`; that matches parser aliases but is less clear than `--off`/`--on`.
- Input validation is uneven across object types. Ports and pkeys parse integers and bound high values, while interface names and file regexes rely mostly on libsemanage acceptance.
- Audit logging uses `audit.audit_encode_nv_string()` in fcontext paths, but if the fallback logger is active the `audit` module name may not exist; these fcontext methods still refer to `audit` directly and can fail when the audit import failed.

## Test signals
`test-semanage.py` covers common fcontext, port, login, user, boolean, list, extract, and import/export paths. Coverage is absent or thin for Infiniband records, interface/node add/modify/delete, module enable/disable/remove, permissive domains, dontaudit, alternate stores, `--noreload`, audit fallback behavior, error-path typos, and fcontext equivalence conflict handling. Meaningful integration tests require root-like privileges, SELinux enabled/enforcing, libsemanage Python bindings, setools, sepolicy, and a mutable test policy store.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/python/semanage/seobject.py -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/python/semanage/test-semanage.py -->
# sources/security-integrity/selinux/python/semanage/test-semanage.py

## Purpose
This file is an integration-style unittest harness for the installed `semanage` command. It verifies that selected semanage subcommands can list, extract, export/import, and perform several add/modify/delete cycles against a live enforcing SELinux system.

## Important APIs, types, and functions
- `object_list` enumerates tested subcommands: login, user, port, module, interface, node, fcontext, boolean, permissive, and dontaudit.
- `SemanageTests` contains helper assertions and test methods.
- `test_extract()`, `test_input_output()`, `test_list()`, `test_list_c()`, `test_fcontext()`, `test_fcontext_e()`, `test_port()`, `test_login()`, `test_user()`, and `test_boolean()` execute command subprocesses.
- `semanage_suite()`, `semanage_custom_suite()`, and `semanage_run_test()` build and run unittest suites.
- `CheckTest` validates names passed to `-t/--test`.
- `gen_semanage_test_args()` installs the script's own CLI.

## Control flow
When run as a script, it imports `selinux`, builds `semanage_test_list` from methods beginning with `test_`, and only enables argument parsing when SELinux is enabled and enforcing. The user can list tests, run all tests, or run selected test names. Each test uses `subprocess.Popen` to invoke real system commands, waits with `communicate()`, and asserts status with helper methods.

## State and persistence behavior
The tests deliberately mutate the live system policy store and user database. They create and delete file context mappings for `/ha-web`, fcontext equivalence mappings for `/myhome` and `/myhome1`, TCP port 55 mappings, a Linux user `testlogin`, an SELinux user `testuser_u`, a login mapping, and `httpd_anon_write` boolean state. Export writes `/tmp/out` and import replays it. Cleanup commands are issued before many tests but are best-effort and sometimes do not assert cleanup success.

## Dependencies and integration points
The harness depends on Python `unittest`, `argparse`, `sys`, and `subprocess`, plus installed host commands `semanage`, `useradd`, `userdel`, and a Python `selinux` module. It requires SELinux enforcing mode, policy names such as `targeted`, roles/types such as `staff_r`, `staff_u`, `ssh_port_t`, `http_port_t`, `httpd_sys_content_t`, and boolean `httpd_anon_write`.

## Risks and edge cases
- These are destructive integration tests against the current machine, not isolated unit tests.
- Some subprocesses capture only stdout or only stderr, and many ignore output from cleanup operations.
- `assertSuccess()` and `assertFailure()` use `assertTrue` with static strings, so diagnostics can omit command context.
- `test_fcontext_e()` prints "Verify semanage fcontext -m -e" but runs `-a -e` for `/myhome1`; modify-equivalence behavior is not actually tested.
- `test_login()` does not assert success for the `semanage login -d` cleanup in the main test path.
- `assertDenied()` and `assertNotFound()` are unused.
- The test set omits ibpkey, ibendport, interface mutation, node mutation, module add/remove/enable/disable, permissive mutation, dontaudit, failure modes, and parser conflict validation.

## Test signals
Passing this suite indicates basic installed-command functionality on a permissive test host with the expected policy vocabulary. It is not suitable for normal unprivileged CI unless run inside a disposable SELinux-enabled environment.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/python/semanage/test-semanage.py -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/python/sepolgen/Makefile -->
# sources/security-integrity/selinux/python/sepolgen/Makefile

## Purpose
This top-level sepolgen makefile delegates build lifecycle targets to subdirectories. It is a thin coordinator for the `src` and `tests` trees.

## Important APIs, types, and functions
Targets are `all`, `install`, `relabel`, `clean`, and `test`. `all` and `relabel` are no-ops. `install` delegates to `src`. `clean` delegates to `src` and `tests`, then removes local editor, bytecode, and parser generated files. `test` delegates to `tests`.

## Control flow
Make invokes the named target. Delegated targets use `$(MAKE) -C <dir> $@`, preserving the original target name.

## State and persistence behavior
`install` persists files only through the `src` sub-make. `clean` removes `*~`, `*.pyc`, `parser.out`, and `parsetab.py` in this directory after cleaning child directories.

## Dependencies and integration points
It depends on GNU/POSIX make semantics, `src/Makefile`, and `tests/Makefile`. The target names must match subdirectory makefiles.

## Risks and edge cases
There is no default build work in `all`, so packaging must know install is the meaningful target. If `tests/Makefile` is missing, `make clean` and `make test` fail even though source installation might be usable.

## Test signals
`make test` is the only test signal and is delegated entirely to `tests`.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/python/sepolgen/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/python/sepolgen/src/Makefile -->
# sources/security-integrity/selinux/python/sepolgen/src/Makefile

## Purpose
This makefile coordinates installation and cleanup for sepolgen source components under `src`.

## Important APIs, types, and functions
Targets are `all`, `install`, `relabel`, `clean`, and `test`. `install` delegates to `sepolgen` and `share`. `clean` delegates to the same two subdirectories and removes local generated/parser/editor/bytecode files. `all`, `relabel`, and `test` are no-ops.

## Control flow
Make routes `install` or `clean` to child directories via `$(MAKE) -C sepolgen $@` and `$(MAKE) -C share $@`.

## State and persistence behavior
`install` writes through child makefiles. `clean` deletes local `*~`, `*.pyc`, `parser.out`, and `parsetab.py` after child cleanup.

## Dependencies and integration points
It requires `src/sepolgen/Makefile` and `src/share/Makefile`. It is invoked by the top-level sepolgen makefile and probably by package build scripts.

## Risks and edge cases
`test` is a no-op here, so top-level tests must come from `tests`, not `src`. The makefile assumes `share` exists and supports matching targets.

## Test signals
No direct tests are run from this makefile.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/python/sepolgen/src/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/python/sepolgen/src/sepolgen/Makefile -->
# sources/security-integrity/selinux/python/sepolgen/src/sepolgen/Makefile

## Purpose
This makefile installs the Python `sepolgen` package files into the configured Python purelib directory and cleans generated artifacts.

## Important APIs, types, and functions
- Variables: `PREFIX ?= /usr`, `PYTHON ?= python3`, `PYTHONLIBDIR ?= $(shell $(PYTHON) -c ...)`, and `PACKAGEDIR ?= /$(PYTHONLIBDIR)/sepolgen`.
- `install` creates `$(DESTDIR)$(PACKAGEDIR)` and installs `*.py` with mode `644`.
- `clean` removes parser artifacts, editor backups, bytecode, and `__pycache__`.

## Control flow
`PYTHONLIBDIR` is computed with `sysconfig.get_path('purelib', vars={'platbase': PREFIX, 'base': PREFIX})`. `install` depends on `all`, then runs `mkdir` and `install`.

## State and persistence behavior
The install target writes Python source files to the destination package directory. `clean` deletes local generated state but does not remove installed files.

## Dependencies and integration points
It depends on Python's `sysconfig`, shell tools `mkdir`, `install`, and `rm`, and packaging variables `DESTDIR`, `PREFIX`, and `PYTHON`. Parent makefiles delegate to it.

## Risks and edge cases
`PACKAGEDIR` includes a leading slash before `$(PYTHONLIBDIR)`. Because `PYTHONLIBDIR` is normally absolute, this yields a double slash in paths such as `//usr/lib/...`, which is usually harmless but untidy. The install command copies every `*.py` in the directory and has no package manifest filtering.

## Test signals
No direct tests are defined. Installation can be smoke-tested by importing `sepolgen` from the target environment.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/python/sepolgen/src/sepolgen/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/python/sepolgen/src/sepolgen/__init__.py -->
# sources/security-integrity/selinux/python/sepolgen/src/sepolgen/__init__.py

## Purpose
This is an empty package initializer for `sepolgen`. Its presence marks the directory as an importable Python package in Python versions and packaging contexts that still require `__init__.py`.

## Important APIs, types, and functions
It defines no public names, functions, classes, or side effects.

## Control flow
No code executes when imported beyond normal module initialization.

## State and persistence behavior
No state is stored or persisted.

## Dependencies and integration points
Other modules import this package namespace, such as `sepolgen.access`, `sepolgen.audit`, `sepolgen.defaults`, and `sepolgen.interfaces`. The makefile installs it with other `*.py` files.

## Risks and edge cases
The empty initializer intentionally does not expose convenience imports. Code must import concrete submodules directly.

## Test signals
A package import smoke test is sufficient: `import sepolgen` should succeed when the package path is installed.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/python/sepolgen/src/sepolgen/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/python/sepolgen/src/sepolgen/access.py -->
# sources/security-integrity/selinux/python/sepolgen/src/sepolgen/access.py

## Purpose
This module defines core in-memory representations for SELinux access: single access vectors, deduplicated access-vector sets, and role-type statements. It is a foundational sepolgen data model used by audit parsing, interface matching, and policy generation.

## Important APIs, types, and functions
- `is_idparam(id)` identifies interface parameters of the form `$N`.
- `AccessVector` stores `src_type`, `tgt_type`, `obj_class`, permissions, audit messages, audit2why rule type, auxiliary data, extended permissions, and information-flow direction. Key methods are `from_list()`, `to_list()`, `merge()`, `to_string()`, and `_compare()`.
- `avrule_to_access_vectors(avrule)` expands a refpolicy AVRule with multiple source types, target types, or object classes into individual `AccessVector` objects.
- `AccessVectorSet` stores non-overlapping vectors in nested dictionaries by source, target, and `(object class, audit2why type)`. It exposes iteration, length, `to_list()`, `from_list()`, `add()`, and `add_av()`.
- `avs_extract_types()` collects source and target types from vectors.
- `avs_extract_obj_perms()` maps object classes to all permissions observed for that class.
- `RoleTypeSet` deduplicates `role types` statements by role and accumulates types.

## Control flow
`AccessVector.from_list()` treats the first three list elements as source, target, and class, and all remaining elements as permissions. `AccessVectorSet.add()` builds an `AccessVector` from explicit arguments and delegates to `add_av()`. `add_av()` creates the nested dictionary buckets and either merges permissions/xperms into an existing vector with the same key or stores the new vector. Audit messages are appended to the merged vector when supplied.

## State and persistence behavior
All state is in-memory. `to_list()`/`from_list()` provide a simple serialization shape for other modules to write/read, but this module performs no file I/O. Merging mutates permission and extended-permission sets in existing vectors.

## Dependencies and integration points
It imports local `refpolicy` and `util`, and `selinux.audit2why`. The module expects `refpolicy.IdSet`, `refpolicy.XpermSet`, and `refpolicy.RoleType`. `audit.py` creates `AccessVector` instances from AVC records. `interfaces.py` uses `is_idparam()`, `avrule_to_access_vectors()`, and `AccessVectorSet` for interface analysis and expansion.

## Risks and edge cases
- `AccessVector.__init__` sets `self.__hash__ = None` on the instance, which does not actually make the class unhashable in the same way as defining `__hash__ = None` at class scope.
- `AccessVectorSet.add()` uses `data=[]` as a default argument. It assigns the list to each created vector, so callers that mutate shared default data could leak state.
- `AccessVectorSet.__len__()` is O(N) over nested maps.
- `AccessVector.merge()` merges permissions and xperms but does not merge metadata such as `data`, `type`, or `info_flow_dir`; this is intentional for same-key vectors but can hide differences if callers expect full provenance.
- `avrule_to_access_vectors()` copies `perms` but not other AVRule metadata.

## Test signals
Focused tests should cover list round-tripping, permission merging, xperm merging, separate buckets for different audit2why types, `is_idparam()` validation, AVRule expansion, and extraction helpers. No tests are present in this subset.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/python/sepolgen/src/sepolgen/access.py -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/python/sepolgen/src/sepolgen/audit.py -->
# sources/security-integrity/selinux/python/sepolgen/src/sepolgen/audit.py

## Purpose
This module obtains and parses SELinux-related audit messages, converts AVC denials/grants and invalid SID messages into sepolgen access and role-type models, and optionally filters them. It bridges host audit logs, kernel messages, `audit2why`, and policy-generation input structures.

## Important APIs, types, and functions
- `get_audit_boot_msgs()`, `get_audit_msgs()`, and `get_dmesg_msgs()` run `/sbin/ausearch` or `/bin/dmesg` and return decoded text.
- `AuditMessage` is the base parser for audit headers.
- `InvalidMessage`, `PathMessage`, `AVCMessage`, `PolicyLoadMessage`, `DaemonStartMessage`, and `ComputeSidMessage` represent specific SELinux/audit record types.
- `AVCMessage.from_split_string()` parses source/target contexts, class, command, executable, name, ioctl command, access set, denial/grant status, and calls `analyze()`.
- `AVCMessage.analyze()` caches `audit2why.analyze()` results in global `avcdict` and converts several audit2why error types to `ValueError`.
- `AuditParser` stores parsed messages, supports last-policy-load-only resets, groups records by audit header, attaches AVC_PATH paths to matching AVCs, and exposes `parse_file()`, `parse_string()`, `to_role()`, and `to_access()`.
- `AVCTypeFilter` and `ComputeSidTypeFilter` include messages whose source, target, or invalid type matches a regex.

## Control flow
Message collection helpers shell out to audit/dmesg commands. Parsing splits each input line into whitespace records, scans for SELinux-related markers, instantiates the appropriate message class, and asks it to parse the same split records. High-level parsing stores recognized messages by class; `PolicyLoadMessage` or auditd `DaemonStartMessage` can reset accumulated state when `last_load_only` is enabled. After parsing, `__post_process()` uses shared audit headers to copy `AVC_PATH` paths onto AVC messages. `to_access()` filters AVCs, skips granted records by default, creates `access.AccessVector` objects, attaches audit2why metadata and ioctl xperms, then adds them to an `AccessVectorSet`.

## State and persistence behavior
Parser state is in-memory: message lists, `by_header`, and `check_input_file`. The module-level `avcdict` caches audit2why analysis results by source context, target context, class, and access tuple. There is no persistence, but host reads depend on `/proc/uptime`, audit logs, and dmesg. `parse_file()` exits the process with status 0 after printing "Nothing to do" if no SELinux-related records were found.

## Dependencies and integration points
The module imports `re`, `sys`, local `refpolicy`, `access`, and `util`, plus `selinux.audit2why`. It calls `/sbin/ausearch` and `/bin/dmesg` through `subprocess`. It depends on `refpolicy.SecurityContext` parsing and `access.AccessVectorSet`/`RoleTypeSet`.

## Risks and edge cases
- `get_audit_boot_msgs()` has `fd.close` without parentheses, so the `/proc/uptime` descriptor is not explicitly closed.
- `AuditParser.__parse_line()` creates `DaemonStartMessage(list)` instead of passing the line string; this stores the built-in `list` object as the raw message.
- `AVCMessage.analyze()` checks `BADSCON` twice; the second branch message says "Invalid Type Class" and probably intended a different audit2why constant.
- Parsing is whitespace-oriented and only handles the subset of audit fields this module needs. Quoted values with embedded spaces or unusual audit formatting can be lost.
- `parse_file()` calls `sys.exit(0)` on no input, making the parser awkward as a library in callers that expect an empty result.
- The global analysis cache is unbounded and process-global.
- Errors from missing `/sbin/ausearch` or `/bin/dmesg` propagate from `subprocess.Popen`.

## Test signals
Useful tests would feed sample AVC, granted AVC, AVC_PATH, MAC_POLICY_LOAD, DAEMON_START, and security_compute_sid lines into `parse_string()`, verify list resets with `last_load_only`, verify path post-processing by audit header, and check `to_access()` output including ioctl xperms. Host command helpers require privileged/system integration tests or subprocess mocking.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/python/sepolgen/src/sepolgen/audit.py -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/python/sepolgen/src/sepolgen/classperms.py -->
# sources/security-integrity/selinux/python/sepolgen/src/sepolgen/classperms.py

## Purpose
This script parses m4-style permission macro definitions from `all_perms.spt`. It appears to be a development utility or experiment rather than a reusable library module, because it performs file I/O and parsing at import time and prints the result.

## Important APIs, types, and functions
- Lexer tokens include `DEFINE`, `NAME`, quotes/backticks, braces, semicolon, parentheses, and comma.
- `t_NAME()` recognizes identifiers and maps `define` to the reserved `DEFINE` token.
- Parser productions `p_statements`, `p_define_stmt`, `p_list`, and `p_names` parse forms such as `define(\`foo',\`{ read write }')` into `[name, permission_list]` pairs.
- `p_error()` prints syntax errors.
- The module initializes local `lex` and `yacc` parsers and then parses `all_perms.spt`.

## Control flow
Importing the module builds the lexer and parser, opens `all_perms.spt` relative to the current working directory, reads it, parses it through `yacc.parse(txt)`, and prints the resulting parsed structure. The defined grammar can parse a single name or a brace-delimited list in each macro body.

## State and persistence behavior
The module reads `all_perms.spt` and writes parsed output to stdout. Parser generation may also create PLY artifacts such as `parser.out` and `parsetab.py`, depending on local `lex`/`yacc` behavior. It does not persist parsed data itself.

## Dependencies and integration points
It imports local `lex` and `yacc` modules, and `sys` though `sys` is unused. It assumes the current working directory contains `all_perms.spt`. The clean targets in the makefiles remove `parser.out` and `parsetab.py`, which are likely generated by this parser.

## Risks and edge cases
- Import-time execution makes this unsafe as a normal package module; importing it will fail if `all_perms.spt` is absent and will print to stdout if present.
- `p_statements()` returns `[p[1]] + [p[2]]` for recursive statements, creating nested lists rather than flattening; this may or may not be intended.
- `p_error()` assumes `p` is not `None`; EOF syntax errors can raise another exception.
- The grammar only accepts simple identifiers and simple macro shape, not broader m4 syntax.
- `t_ignore` includes newlines, so line numbers may not be accurate unless the lexer tracks them elsewhere.

## Test signals
Tests should parse known `define` snippets, check brace and single-name outputs, assert missing/malformed input behavior, and verify the module is not imported accidentally by package-level smoke tests. No tests are included here.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/python/sepolgen/src/sepolgen/classperms.py -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/python/sepolgen/src/sepolgen/defaults.py -->
# sources/security-integrity/selinux/python/sepolgen/src/sepolgen/defaults.py

## Purpose
This module centralizes default filesystem paths for sepolgen data, generated interface metadata, permission maps, attributes, reference-policy makefiles, and include headers. It also provides a configurable search-path helper.

## Important APIs, types, and functions
- `PathChooser(pathname)` reads a simple `key = value` configuration file or installs default `SELINUX_DEVEL_PATH` values when the config file is absent.
- `PathChooser.__call__(testfilename, pathset="SELINUX_DEVEL_PATH")` searches the configured colon-separated path list for `testfilename`, returning the first existing path or a fallback under the first configured directory.
- `data_dir()`, `perm_map()`, `interface_info()`, and `attribute_info()` return `/var/lib/sepolgen` paths.
- `refpolicy_makefile()` uses `PathChooser("/etc/selinux/sepolgen.conf")` to locate `Makefile`, falling back to `include/Makefile`.
- `headers()` locates the reference-policy `include` directory.

## Control flow
Constructing `PathChooser` either sets default search paths or parses each nonblank, noncomment config line with a `key = value` regex. Calling the object splits the selected pathset on `:`, tests each candidate path with `os.path.exists()`, and returns the first hit.

## State and persistence behavior
The object stores parsed configuration in memory and performs no writes. The module reads `/etc/selinux/sepolgen.conf` when helper functions construct a chooser.

## Dependencies and integration points
It imports `os` and `re`. Other sepolgen modules can call these helpers to find installed data under `/var/lib/sepolgen` and reference-policy development files under `/usr/share/selinux/default`, `/usr/share/selinux/mls`, or `/usr/share/selinux/devel` unless overridden by config.

## Risks and edge cases
- Config parsing rejects any nonblank/noncomment line that is not exactly `word = value` shaped.
- Missing pathsets raise `ValueError`; missing files return a best-effort path under the first configured directory, so callers must check existence if required.
- A new `PathChooser` is constructed on every `refpolicy_makefile()` or `headers()` call; there is no cache.
- Defaults are hard-coded Linux distribution paths.

## Test signals
Unit tests can create temporary config files, verify default behavior when absent, check invalid-line errors, and test search precedence. Filesystem integration tests can verify `refpolicy_makefile()` fallback from `Makefile` to `include/Makefile`.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/python/sepolgen/src/sepolgen/defaults.py -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/python/sepolgen/src/sepolgen/interfaces.py -->
# sources/security-integrity/selinux/python/sepolgen/src/sepolgen/interfaces.py

## Purpose
This module models SELinux reference-policy interfaces and templates as access-vector summaries. It extracts parameter types, expands nested interface calls, merges attribute-derived access, and indexes interfaces by target type for later matching and policy generation.

## Important APIs, types, and functions
- `Param` stores an interface parameter name like `$1`, its field type (`SRC_TYPE`, `TGT_TYPE`, `OBJ_CLASS`, `ROLE`, or `DEST_TYPE`), related object classes, and whether it is required.
- `__param_insert()` records inferred parameter usage and reports conflicts, promoting ambiguous source/target parameters to source type for implicitly typed objects.
- `av_extract_params()`, `role_extract_params()`, `type_rule_extract_params()`, and `ifcall_extract_params()` infer parameter roles from access vectors, role statements, type rules, and interface calls.
- `AttributeVector` and `AttributeSet` store attribute-to-access summaries and can load them from a bracketed flat file format.
- `InterfaceVector` summarizes one parsed interface/template, including `enabled`, `name`, `access`, `params`, and expansion state. `from_interface()` consumes refpolicy objects and optional attribute summaries.
- `InterfaceSet` stores all vectors, serializes/deserializes them with `to_file()`/`from_file()`, builds target-type indexes, adds headers, maps parameters through calls, and expands nested calls.

## Control flow
`InterfaceVector.from_interface()` iterates parsed interface AV rules, keeps only allow rules, skips suspicious allow rules in `dontaudit`-named interfaces, expands each AV rule into `AccessVector` instances, and adds them while extracting parameter metadata. It then folds in typeattribute-derived access by replacing attribute names with concrete types. Finally it scans roles, type rules, and nested interface calls for additional parameter usage.

`InterfaceSet.add_headers()` adds every interface and template from a parsed headers object, expands nested interface calls, and builds indexes. Expansion is depth-first: `do_expand_ifcalls()` starts at one interface, walks called interfaces/templates through a stack, maps `$N` parameters to actual call arguments with `map_param()`, and adds the called interface's access to the caller vector with `map_add_av()`. Circular self-calls are detected only when a direct call targets the original interface name.

## State and persistence behavior
Most state is in-memory: dictionaries of interfaces, target-type indexes, and expanded access vectors. `to_file()` and `from_file()` support persistence through a plain text format with `[InterfaceVector ...]` headers and comma-joined access-vector rows. `AttributeSet.from_file()` reads a similar format for attributes. No writes occur except through the caller-provided file object in `to_file()`.

## Dependencies and integration points
The module imports `copy`, `itertools`, and local `access`, `refpolicy`, `objectmodel`, `matching`, and `sepolgeni18n._`. `matching` is imported but unused in this file. It depends on parsed refpolicy header objects exposing `interfaces()`, `templates()`, `avrules()`, `roles()`, `typerules()`, `typeattributes()`, and `interface_calls()`. It uses `objectmodel.implicitly_typed_objects` to resolve source/target parameter ambiguity.

## Risks and edge cases
- `InterfaceVector.__init__(..., attributes={})`, `from_interface(..., attributes={})`, and `InterfaceSet.add(..., attributes={})` use mutable default dictionaries. They are not mutated here, but the pattern is risky.
- `InterfaceSet.from_file()` returns `None` from `parse_ifv()` when a header has no params; the following access rows are then ignored because `ifv` is false.
- `AttributeSet.from_file()` and `InterfaceSet.from_file()` index `line[0]` without guarding against blank lines.
- `do_expand_ifcalls()` only checks direct calls back to the root interface. Longer cycles can keep pushing calls until already-expanded markers happen to stop descent, and incomplete expansion ordering can hide some recursive access.
- `map_add_av()` uses one `new_perms` set for all source/target/class combinations. That is efficient for normal mappings but assumes permission parameter expansion is independent of the mapped class.
- Conflicts detected by parameter extraction are silently ignored with `pass`, losing diagnostics that would help explain poor matches.

## Test signals
Tests should cover parameter inference from access vectors/type rules/roles/interface calls, ambiguous implicit object handling, serialization round-trips, target-type indexing, nested interface expansion, optional-parameter dropping, attribute replacement, circular-call detection, blank-line parsing, and direct no-parameter interface loading.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/python/sepolgen/src/sepolgen/interfaces.py -->
