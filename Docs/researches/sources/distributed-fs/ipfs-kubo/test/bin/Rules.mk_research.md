# sources/distributed-fs/ipfs-kubo/test/bin/Rules.mk

Purpose: makefile fragment that builds Go-based test helper binaries into `test/bin` and adds that directory to PATH for the test harness. It defines a reusable `go-build-testdep` recipe that changes into `test/dependencies` and runs `$(GOCC) build $(go-flags-with-tags) -o "$OUT" "$<"`.

Important targets: `pollEndpoint`, `go-sleep`, `go-timeout`, `iptb`, `ma-pipe-unidir`, `json-to-junit`, `gotestsum`, `hang-fds`, `multihash`, `cid-fmt`, `random-data`, `random-files`, `gocovmerge`, and `golangci-lint`. Each target is declared `.PHONY` against its Go import path, maps to `$(d)/binary-name`, appends itself to `TGTS_$(d)`, and depends on `$(DEPS_GO)` through the aggregate rule.

Control flow is standard make expansion: include `mk/header.mk`, accumulate targets, declare cleanup with `CLEAN += $(TGTS_$(d))`, prepend `$(realpath $(d))` to PATH, and include `mk/footer.mk`. State is the generated helper binaries; cleanup is delegated to the larger make system. Risks include network/module resolution if dependencies are not vendored or cached, PATH shadowing from generated helpers, and brittle import-path target names if dependencies move. Test signal is indirect: many sharness/CLI tests rely on these helpers being present.
