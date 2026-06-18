<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-pull-metalink.sh -->
# sources/cloud-native/ostree/tests/test-pull-metalink.sh

## Purpose
`test-pull-metalink.sh` validates pulling via a metalink remote, including summary discovery, alternate URL fallback, hash/size verification, malformed metalink errors, and parsing with irrelevant nested elements.

## Important APIs, Types, And Functions
The script uses `OSTREE_HTTPD`, `setup_fake_remote_repo1`, generates `metalink.xml`, computes MD5/SHA256/SHA512 and size for `summary`, configures `remote add ... metalink=URL`, runs `pull`, `remote refs`, and helper `test_metalink_pull_error`.

## Control Flow
It starts a second HTTP server for metalink data, creates a metalink with bad and missing URLs before the valid summary URL to test fallback, pulls successfully, and checks remote refs. It then mutates the metalink for invalid hash format, wrong checksum, wrong size, missing verification, missing URL, malformed XML, and nested unknown elements.

## State And Persistence
State includes metalink XML files, copied original summaries, a bad summary file, local repos recreated between negative tests, and HTTP server port/address files.

## Dependencies And Integration Points
It integrates metalink XML parsing, HTTP fallback selection, summary verification, remote refs discovery through `ostree_repo_remote_fetch_summary`, and pull.

## Risks And Test Signals
The test is XML and diagnostic sensitive. Passing signals include successful fallback to the valid URL, correct `main` refs, and specific failures for hash, checksum, size, verification, URL, and malformed document cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-pull-metalink.sh -->
