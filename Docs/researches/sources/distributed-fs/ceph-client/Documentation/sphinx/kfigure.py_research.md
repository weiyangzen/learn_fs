<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/sphinx/kfigure.py -->
# sources/distributed-fs/ceph-client/Documentation/sphinx/kfigure.py

## Purpose
Sphinx extension that adds kernel-specific image, figure, and render directives. It chooses builder-appropriate output formats for DOT and SVG assets, generating SVG for HTML, PDF for LaTeX, or falling back to literal source when conversion tools are unavailable.

## Important APIs, Types, And Functions
- Directives: `KernelImage` (`kernel-image`), `KernelFigure` (`kernel-figure`), and `KernelRender` (`kernel-render`).
- Node classes: `kernel_image`, `kernel_figure`, and `kernel_render`.
- `setupTools()` discovers `dot`, `inkscape`, `convert`, and `rsvg-convert`, including Inkscape option compatibility.
- `convert_image()` rewrites image URIs/candidates and dispatches conversion based on source extension and builder format.
- `dot2format()`, `svg2pdf()`, and `svg2pdf_by_rsvg()` wrap external conversion commands.
- `add_kernel_figure_to_std_domain()` registers caption labels for `kernel-figure` with Sphinx's standard domain.

## Control Flow
During builder initialization, tool paths are probed and stored in module globals. Directive parsing rejects remote URIs and glob patterns, delegates baseline parsing to docutils image/figure logic, and wraps the resulting node. Visitor hooks later call `convert_image()` during output generation. `kernel-render` stores directive body text as a deterministic hashed temporary asset under the builder image directory before converting it through the same image path.

## State And Persistence
The extension writes generated DOT/SVG/PDF artifacts under the Sphinx output tree and skips regeneration when destination ctime is newer than the source. Tool availability is cached in globals for the whole build. It mutates `translator.builder.images` to avoid duplicate image-copy behavior after conversion.

## Dependencies And Integration Points
Depends on docutils image/figure directives, Sphinx translators/builders, Graphviz `dot`, Inkscape, ImageMagick `convert`, and librsvg `rsvg-convert`. It integrates with HTML, LaTeX, texinfo, text, and man builders, and with Sphinx standard-domain labels for cross references.

## Risks And Edge Cases
Conversion behavior depends on host toolchain versions and can silently degrade to literal blocks. `which()` only checks `path.isfile()` and not executable permission. `isNewer()` compares ctime rather than mtime, which may miss or over-trigger rebuilds under some filesystem operations. Hashing render body only ignores directive attributes, so semantically different render options can share an intermediate asset.

## Test Signals
Build documentation with and without Graphviz/SVG conversion tools, for HTML and LaTeX builders. Verify DOT-to-SVG/PDF, SVG-to-PDF, literal fallback, rejected remote/glob URIs, stable render filenames, and working `:ref:` links to `kernel-figure` captions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/sphinx/kfigure.py -->
