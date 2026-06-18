# sources/cloud-native/moby/integration/container/links_linux_test.go

Purpose: Linux legacy-link and host-network checks for `/etc/hosts` content and linked-container names in list output.

Important APIs and flow: `TestLinksEtcHostsContentMatch` reads host `/etc/hosts`, runs a host-network container, cats `/etc/hosts` inside it, and expects exact content equality. `TestLinksContainerNames` runs two named containers, links the second to the first, lists containers filtered by the first name, and verifies the names include both the direct name and link alias path.

State and dependencies: Uses host network mode, local host filesystem, legacy links, and container list metadata. Skips remote daemon and Windows where unsupported.

Risks and signals: It guards legacy link name reporting and host network file behavior. Failures may break compatibility for old link-based workflows or indicate host-network mount/content changes.
