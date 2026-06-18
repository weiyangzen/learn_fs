# sources/cloud-native/ostree/man/ostree-summary.xml

Purpose: This DocBook refentry documents `ostree summary`, the command for regenerating or viewing the optional repository `summary` metadata file. It explains that summaries describe available branches and enable atomic metadata updates across multiple commits.

Important APIs and commands: The synopsis exposes two modes: update mode with `--update/-u`, optional `--add-metadata/-m KEY=VALUE`, GPG signing options `--gpg-sign` and `--gpg-homedir`, and generic signing options `--sign` plus `--sign-type`; and read mode with mutually required `--view/-v` or `--raw`. Additional metadata values must use GVariant text format and namespaced keys.

Control flow and state: Update mode writes repository metadata. If a collection ID is configured, it also updates the `ostree-metadata` branch for that collection ID with a commit containing the metadata, signed when the summary is signed. View and raw modes only read persisted summary bytes.

Dependencies and integration points: Depends on repository refs, summary file serialization, GVariant metadata parsing, GPG signing, newer signature engines such as ed25519/dummy, and collection ID metadata branch handling. The command is central to remote clients, static delta publication, and peer-to-peer metadata discovery.

Risks: Metadata parsing is user-sensitive because malformed GVariant text or unnamespaced keys can create hard-to-debug repository metadata. Signing behavior spans legacy GPG and newer sign API engines, so docs can drift from implementation defaults. Collection-ID side effects mean `--update` changes more than the single `summary` file in configured repos.

Test signals: CLI tests should cover `summary -u`, repeated `--add-metadata`, `--view`, `--raw`, signed summaries, and collection-ID repositories where the metadata branch is updated. Golden-output tests can validate the human-readable summary format shown in the example.
