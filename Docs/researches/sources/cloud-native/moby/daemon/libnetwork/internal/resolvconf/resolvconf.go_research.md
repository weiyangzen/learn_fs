# sources/cloud-native/moby/daemon/libnetwork/internal/resolvconf/resolvconf.go

## Purpose
Implements parsing, mutation, transformation, generation, and write/hash tracking for container `/etc/resolv.conf` content. It is the core DNS configuration adapter between host resolver state, Docker CLI DNS overrides, legacy networking, and networks with Docker's internal resolver.

## Important APIs, Types, And Functions
- `ResolvConf` stores parsed nameservers, search domains, options, unknown directives, and construction metadata.
- `ExtDNSEntry` records nameservers removed from the generated container file for use by the internal DNS resolver, including whether a loopback address must be reached from the host namespace.
- `Load` and `Parse` read resolv.conf from a path or reader, preserve source path metadata, parse only known directives into structured fields, keep unknown directives verbatim, and wrap scanner errors as `systemError`.
- `OverrideNameServers`, `OverrideSearch`, `OverrideOptions`, `AddOption`, and accessors mutate or expose DNS fields. Accessors clone slices to avoid external mutation.
- `TransformForLegacyNw` removes host-loopback nameservers and IPv6 nameservers when IPv6 is disabled, then falls back to Google public DNS defaults if no usable nameserver remains.
- `TransformForIntNS` replaces all nameservers with the internal resolver address, stashes previous nameservers in metadata, and ensures required resolver options such as `ndots`.
- `Generate` writes resolv.conf syntax plus optional diagnostic comments about source, transform, overrides, invalid nameservers, external servers, warnings, and ndots provenance.
- `WriteFile` writes the generated file and optional digest hash; `UserModified` compares the current file against that digest.
- `removeInvalidNDots` filters malformed `ndots` values when an internal resolver requires a valid setting.

## Control Flow
Parsing scans line by line, strips blank/comment lines, uses `strings.Fields`, and handles `nameserver`, `search`/`domain`, and `options`. Invalid nameserver tokens are not fatal; they are remembered for diagnostics. Legacy transformation is skipped when nameservers were explicitly overridden. Internal resolver transformation always moves existing nameservers to `ExtNameServers`, sets the only configured nameserver to the internal address, and conditionally adds required options without overwriting valid existing options.

## State And Persistence
Most state is in-memory on `ResolvConf`. Persistent effects happen only in `WriteFile`, which truncates/writes the target resolv.conf because it may be bind-mounted, and writes the hash atomically through `atomicwriter`. `UserModified` treats a missing hash file as "not modified yet" but reports unreadable or unparsable hashes as errors.

## Dependencies And Integration Points
Uses `net/netip` for address parsing, `opencontainers/go-digest` for modification detection, `moby/sys/atomicwriter` for hash updates, and containerd logging for fallback warnings. It integrates with libnetwork sandbox setup, the embedded resolver path, and user DNS override handling.

## Risks
The parser intentionally accepts unknown directives and invalid nameservers, so downstream users must rely on generated diagnostics rather than hard failures. `WriteFile` is not atomic for the resolv.conf target itself because bind mounts prevent rename-based replacement. Metadata such as `HostLoopback` depends on whether the nameservers came from host config or override, so incorrect override tracking could make the embedded resolver query the wrong namespace.

## Test Signals
`resolvconf_test.go` covers option lookup precedence, file/hash write and user modification detection, override generation golden files, legacy and internal resolver transforms, invalid ndots replacement, source path detection, invalid nameserver comments, unknown directive preservation, header insertion, parse error wrapping for overlong lines, and generation allocation benchmarks.
