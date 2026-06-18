<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-pull-mirrorlist.sh -->
# sources/cloud-native/ostree/tests/test-pull-mirrorlist.sh

## Purpose
`test-pull-mirrorlist.sh` validates pulling from a mirrorlist remote with multiple content mirrors and fallback behavior.

## Important APIs, Types, And Functions
The script uses `OSTREE_HTTPD`, `setup_fake_remote_repo1`, helper `setup_mirror`, deletes selected `.filez` objects from mirrors, writes a `mirrorlist` file, configures a remote with mirrorlist URL, and runs `ostree pull`.

## Control Flow
It creates three content mirrors, removes different objects to force fallback across mirrors, writes a mirrorlist pointing at them, and pulls into fresh repos for several scenarios, including successful fallback and expected errors when mirrors cannot satisfy requests.

## State And Persistence
State includes mirror directories, deleted object files, mirrorlist text, local client repos, and remote config.

## Dependencies And Integration Points
It covers mirrorlist parsing, HTTP object fetch fallback, object integrity validation, and pull retry behavior across multiple base URLs.

## Risks And Test Signals
The test relies on deterministic object selection and HTTP serving. Passing signals include successful pulls when at least one mirror has each object and failures when mirror coverage is insufficient.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-pull-mirrorlist.sh -->
