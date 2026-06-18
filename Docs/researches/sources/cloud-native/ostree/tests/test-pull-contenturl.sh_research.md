<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-pull-contenturl.sh -->
# sources/cloud-native/ostree/tests/test-pull-contenturl.sh

## Purpose
`test-pull-contenturl.sh` verifies remotes whose summary metadata points content fetches at a separate content URL.

## Important APIs, Types, And Functions
It uses an HTTP fixture, optional GPG signing, `setup_fake_remote_repo1`, summary mutation/configuration for content URLs, a separate `httpd-content` server tree, `remote add`, `pull`, `fsck`, and optional verification setup.

## Control Flow
The script starts with an archive remote, prepares separate content hosting, removes or adjusts summary/signature files as needed, initializes a client repo, configures GPG verification based on feature availability, pulls from the remote, and verifies the resulting repo.

## State And Persistence
State includes original metadata server content, separate content URL directory, summary files and signatures, client repo refs/objects, and temporary HTTP server paths.

## Dependencies And Integration Points
It integrates remote summary parsing, contenturl handling, HTTP object fetching, optional GPG summary verification, and fsck.

## Risks And Test Signals
The risk is fetching metadata from one server but content from the wrong location, or breaking signature semantics. Passing signals include successful pull and fsck with content served from the alternate URL.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-pull-contenturl.sh -->
