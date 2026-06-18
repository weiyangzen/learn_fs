<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/sshutil/scpurl.go -->
# sources/cloud-native/buildkit/util/sshutil/scpurl.go

Purpose: detects and parses implicit SCP-style Git SSH URLs such as `git@github.com:moby/buildkit.git`.

Important APIs and types: `IsImplicitSSHTransport`, `SCPStyleURL`, `ParseSCPStyleURL`, and `SCPStyleURL.String`.

Control flow: a regex accepts username, hostname, path, optional query, and optional fragment. Parse builds `url.Userinfo`, host, path, parsed query values, and fragment. String reconstructs the SCP-style URL and appends encoded query and fragment.

State and persistence: pure parsing/formatting.

Dependencies and integration: uses `regexp`, `net/url`, and `pkg/errors`. Integrated by Git source URL handling that distinguishes implicit SSH from explicit transports.

Risks: regex is intentionally narrower than all possible SSH syntaxes; for example explicit `ssh://` URLs are not implicit. Query encoding may reorder query keys through `url.Values.Encode`.

Test signals: `scpurl_test.go` covers accepted/rejected implicit forms and parsing of fragment fields.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/sshutil/scpurl.go -->
