<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/coccinelle.sh -->
## sources/cloud-native/ostree/tests/coccinelle.sh

Purpose: runs semantic-patch blacklist tests over the OSTree source tree using Coccinelle `spatch`.

Important APIs/functions: sources `libtest.sh`, checks `spatch --version`, skips if `OSTREE_UNINSTALLED_SRCDIR` is unset, counts `tests/coccinelle/*.cocci`, and runs each with `spatch --very-quiet --dir`.

Control flow/state: emits a TAP plan based on the number of `.cocci` files, writes each semantic patch result to `cocci.out`, and fails if output is non-empty.

Dependencies/integration: requires uninstalled source checkout and Coccinelle. It integrates with Automake/TAP shell tests through `skip` and `fatal`.

Risks/test signals: shell word splitting over filenames is simple but acceptable for this tree. Main signal is empty `cocci.out` per semantic patch and TAP `ok` lines.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/coccinelle.sh -->
