## sources/distributed-fs/ipfs-kubo/test/sharness/t0012-completion-fish.sh

Purpose: validates generated fish shell completions for the Kubo CLI.

Important control flow: runs `ipfs commands completion fish`, writes/generated completion content, and checks that completion data can complete a representative command such as `ipfs version`. No daemon is required.

State and dependencies: writes temporary completion files in the sharness trash directory. Depends on the built `ipfs` CLI and fish-compatible completion syntax expectations.

Risks: brittle if command completion output format changes or if the test environment lacks assumptions needed to evaluate completions. Test signal is successful generation and expected completion for a known subcommand.
