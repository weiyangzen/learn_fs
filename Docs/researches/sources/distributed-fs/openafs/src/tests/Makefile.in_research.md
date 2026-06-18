# sources/distributed-fs/openafs/src/tests/Makefile.in

## Purpose
`src/tests/Makefile.in` builds the OpenAFS regression test programs and generates runtime path configuration modules/scripts used by the test harness.

## Important APIs, types, and functions
Important targets are `all`, `check`, `check-fast`, `run-tests`, every `TEST_PROGRAMS` binary, `OpenAFS/Dirpath.pm`, `OpenAFS/Dirpath.sh`, `hello-world`, `mountpoint`, `clean`, and `TAGS`. Library groups include `SYS_LIBS`, `AUTH_LIBS`, `INT_LIBS`, and `COMMON_LIBS`.

## Control flow
The default target creates `run-tests`, generated OpenAFS path modules, and many filesystem behavior test binaries. Individual rules link test objects with common err/warn compatibility objects and the appropriate OpenAFS libraries. `OpenAFS/Dirpath.pm` and `.sh` are generated at make time from autoconf variables and distinguish Transarc versus modern paths. `check` and `check-fast` run `./run-tests`.

## State and persistence behavior
It creates executable tests, generated Perl/shell configuration files, and transient objects. Tests themselves may create files, directories, mountpoints, tokens, and cache state when run. `clean` removes generated test artifacts and binaries.

## Dependencies and integration points
It depends on configured OpenAFS libraries, the test harness `run-tests.in`, many C test sources, `fs_lib`, generated dirpath files, and OpenAFS Perl modules under `OpenAFS/`.

## Risks
The long source/object/program lists can drift; `test-parallel1.o` appears twice in `TEST_OBJS`. Generated path files embed installation assumptions and must be regenerated after configure changes. Empty `install`/`dest` targets intentionally avoid installing tests but may surprise packaging automation.

## Test signals
Run `make all`, `make check`, and `make check-fast`; verify `OpenAFS/Dirpath.pm` and `.sh` contain expected configured paths; build with strict dependency checks for every listed test binary.
